# Compare many image files
from typing import Any
from discord.ext.commands import Context
from itertools import combinations
from io import SEEK_END
from binascii import Error

# Image check imports
from sentence_transformers import SentenceTransformer, util
from PIL import Image

from api.loader import to_stream, SourceNotFound, FileTooLarge


# If smbdy can add the rest would be nice thanks
ALLOWED_FORMATS = (
    "png", "jpg", "jpeg", "gif",
    "b64", "arr"
)
model = None


def load_model():
    global model

    # Load the OpenAI CLIP Model
    print('Loading clip-ViT-B-32 Model...')
    model = SentenceTransformer('clip-ViT-B-32')
    print('Model loaded')


def shorten(filename):
    if len(filename) > 10:
        return filename[-10:-1] + "..."
    return filename


def compare(*images):
    if not model:
        load_model()


    # Both are BytesIO objects, so we need to load them in
    encoded_image = model.encode(
        [Image.open(i) for i in images], 
        batch_size=128, convert_to_tensor=True, 
        show_progress_bar=True
    )
    processed_images = util.paraphrase_mining_embeddings(encoded_image)
    score = processed_images[0][0]
    
    return score, (score * 100)


async def compare_images(ctx: Context, *images) -> Any:
    files = []
    for attachment in ctx.message.attachments:
        if attachment.filename.lower().endswith(ALLOWED_FORMATS):
            files.append(attachment.url)

    images = (files + list(images))[:10]

    if len(images) < 2:
        return await ctx.reply(content="You must have 2 or more files to compare")

    try:
        streams = [await to_stream(ctx, arg=im) for im in images]
    except Error:
        return await ctx.reply(content="Invalid base64 string provided")
    except FileTooLarge as exc:
        return await ctx.reply(content=exc.args[0])
    except ValueError:
        return await ctx.reply(content="Cannot parse provided format")
    except SourceNotFound:
        return await ctx.reply(content="Source provided cannot be translated")

    combos = combinations(range(len(images)), 2)

    RESULTS = {}

    for st1, st2 in combos:
        stream1 = streams[st1]
        stream2 = streams[st2]
        PRE = ""

        # Check filesize first
        if not (y1 := stream1.seek(0, SEEK_END)) == (y2 := stream2.seek(0, SEEK_END)):
            PRE = f"Fail ({(z := y1/y2)} [{(z * 100)}%]) - Difference in filesize"
        else:
            PRE = f"Pass (1.0 [100%]) - File sizes are the same"
        stream1.seek(0), stream2.seek(0)

        raw, per = await ctx.bot.loop.run_in_executor(None, compare, stream1, stream2)
        if raw >= 0.999:
            # May be 0.999 due to some lossy compressions
            PRE += f"\nPass ({raw} [{per}%]) - Images are identitical"
        elif raw < 0.999 and raw > 0.5:
            PRE += f"\nMaybe ({raw} [{per}%]) - Images are near identical, they share common features"
        else:
            PRE += f"\nFail ({raw} [{per}%]) - Images are not identical"

        RESULTS[(st1, st2)] = PRE + "\n"

    content = f"Comparison of {len(images)} image files" + "\n```"
    for pair, status in RESULTS.items():
        # Index in streams == index in images
        si1, si2 = pair
        f1, f2 = images[si1], images[si2]
        if f1.startswith("https://cdn.discordapp.com/"):
            f1 = f1.split("/")[-1]
        if f2.startswith("https://cdn.discordapp.com/"):
            f2 = f2.split("/")[-1]

        content += f"\n[{shorten(f1)}] ({si1}) = [{shorten(f2)}] ({si2})\n"
        content += status

    content += "```"
    return await ctx.reply(content=content)


COMMAND_CALLBACK = compare_images
COMMAND_NAME = "compare"
COMMAND_DESCRIPTION = "Check if 2 or more image files are the same"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = f"""\
{COMMAND_DESCRIPTION}

Attaching Files:
  Image files can be attached, as of now bT_CV only supports:
  {", ".join(ALLOWED_FORMATS)}

  Files attached will be appended to args then reduced to 10 items
"""
COMMAND_USAGE = """
ct!compare [src..., : MAX=10]
ct!compare [src..., : MAX=10]?
"""
