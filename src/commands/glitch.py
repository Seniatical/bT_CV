from typing import Any
from discord.ext.commands import Context
from discord import Embed, Colour
from binascii import Error

from api.loader import to_stream, SourceNotFound, FileTooLarge
from api.export import to_file, gen_cache_id
from api.combine import combine
from api.glitcher import glitch_image
from commands.compare import COMMAND_BRIEF, COMMAND_USAGE
from core.com_par import parser
from copy import deepcopy


glitch_prser = deepcopy(parser)
glitch_prser.add_argument(
    "-i", "--intensity", dest="intensity", type=float, default=1.0
)
glitch_prser.add_argument(
    "-c", "--change", dest="change", type=float, default=0.0
)
glitch_prser.add_argument(
    "-gC", "--glitch-cycle", dest="cycle", action="store_true", default=False
)
glitch_prser.add_argument(
    "-cO", "--color-offset", "--colour-offset", dest="offset", action="store_true", default=False
)
glitch_prser.add_argument(
    "-sL", "--scan-lines", dest="scan", action="store_true", default=False
)
glitch_prser.add_argument(
    "-g", "--gif", dest="gif", action="store_true", default=True
)
glitch_prser.add_argument(
    "-gF", "--glitch-frames", dest="gframes", type=int, default=23
)
glitch_prser.add_argument(
    "-s", "--step", dest="step", type=int, default=1
)
glitch_prser.add_argument(
    "-S", "--seed", dest="seed", type=float, default=None
)


def get_glitch_kwds(kwds):
    return {
        "glitch_amount": kwds.pop("intensity"),
        "glitch_change": kwds.pop("change"),
        "gif": kwds.pop("gif"),
        "cycle": kwds.pop("cycle"),
        "color_offset": kwds.pop("offset"),
        "scan_lines": kwds.pop("scan"),
        "frames": kwds.pop("gframes"),
        "step": kwds.pop("step"),
        "seed": kwds.pop("seed")
    }


async def glitch(ctx: Context, source: str = None,
                 *flags
                 ) -> Any:
    prsed = vars(await ctx.bot.loop.run_in_executor(None, glitch_prser.parse_args, flags))
    glitch_kwds = get_glitch_kwds(prsed)

    ## Verify args
    if glitch_kwds["glitch_amount"] < 1:
        glitch_kwds["glitch_amount"] = 1
    elif glitch_kwds["glitch_amount"] > 10:
        glitch_kwds["glitch_amount"] = 10

    if glitch_kwds["frames"] > 50:
        glitch_kwds["frames"] = 50
    elif glitch_kwds["frames"] < 1:
        glitch_kwds["frames"] = 1

    ## Load in image
    try:
        if cache := ctx.bot.runtime_cache["IMAGES"].get(prsed["cache_id"]):
            if cache["priv"] and ctx.author.id != cache["user"]:
                return await ctx.reply(content="Cache item is being guarded!")
            stream = await to_stream(ctx, url=cache["uri"])
        else:
            stream = await to_stream(ctx, arg=source, source_select=prsed["ss"])
    except Error:
        return await ctx.reply(content="Invalid base64 string provided")
    except FileTooLarge as exc:
        return await ctx.reply(content=exc.args[0])
    except ValueError:
        return await ctx.reply(content="Cannot parse provided format")
    except SourceNotFound:
        return await ctx.reply(content="Source provided cannot be translated")

    ## Apply filters if opt == BEFORE
    if prsed["filters"] and prsed["f_group"] == "BEFORE":
        stream, opts, status = combine(stream, prsed["filters"][:5], **prsed)

    def glitch_im():
        return glitch_image(stream, glitch=glitch_kwds, **prsed)
    
    ## Save
    exportable, *opts = await ctx.bot.loop.run_in_executor(None, glitch_im)

    if prsed["filters"] and prsed["f_group"] == "AFTER":
        exportable, opts, status = combine(exportable, prsed["filters"][:5], **prsed)

    kwds = {"pot": prsed["form"], "sf": prsed["skip"]}
    if opts:
        kwds.update({"duration": opts[0], "loop": opts[1]})

    file = to_file(exportable, prsed["export-type"], **kwds)
    getattr(stream, "close", lambda: "")()

    if file.is_image:
        embed = Embed(title="Converted image", colour=Colour.red())
        embed.set_image(url=f"attachment://{file.filename}")
        if prsed["filters"]:
            value = "```\n"
            for i, j in status:
                value += f"{i}:\n"
                value += f"  {j}\n"
            value += "```"
            embed.add_field(name="Filter Statuses", value=value)
        m = await ctx.reply(embed=embed, file=file)
    else:
        m = await ctx.reply(content="Converted image data []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = glitch
COMMAND_NAME = "glitch"
COMMAND_DESCRIPTION = "Glitch an image"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = f"""\
{COMMAND_DESCRIPTION}

Flags:
  -sS --source-select [integer] default=-1
  -E --export [string] [image | base64 | array] default=image
  -iF --image-format [string] [PNG | JPG | GIF | JPEG] default=AUTO
  -C --cache [FLAG] default=False
  -fC --from-cache [string (cache_id)] default=None
  -cP --cache-protect [FLAG] default=False
  -nA --no-animate [FLAG] default=False
  -F --frame [int] default=0
  -f --filter [string] [stack=5] default=[]
  -fG --filter-grouping [string] [BEFORE | AFTER] default=BEFORE
  -r --reverse [FLAG] default=False
  -sF --skip-frame [int] [stack=FRAMES.length] default=[]
  -l --loop [int] default=0[INF]
  -d --duration [int (ms)] default=Image.duration
  -i --intensity [float [RANGE(1, 10)]] default=1.0
  -c --change [float] default=0.0
  -C --cycle [FLAG] default=False
  -cO --[color,colour]-offset [FLAG] default=False
  -sL --scan-lines [FLAG] default=False
  -gF --glitch-frames [int RANGE(1, 50)] default=23
  -s --step [int] default=1
  -S --float [int] default=glitch.random()
  -g --gif [FLAG] default=True
"""
COMMAND_USAGE = """
ct!glitch [src...]
ct!glitch [src...] [--flags, ...]
"""
