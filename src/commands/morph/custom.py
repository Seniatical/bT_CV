"""
Custom morph generator
"""
from ast import literal_eval
from typing import Any, Tuple, List
from discord import Embed, Colour
from discord.ext.commands import Context

from core.com_par import parser
from api.combine import combine
from api.loader import to_stream
from api.export import to_file, gen_cache_id
from api.morph import gen_custom_morph, apply_morph, LUT_RE

from binascii import Error
from api.loader import SourceNotFound, FileTooLarge


def read_from_file(ctx) -> str:
    if not ctx.message.attachments:
        return "No message attachments found"
    file = None
    for i in ctx.message.attachments:
        if i.filename != "patterns.arr":
            continue
        else:
            file = i
            break
    
    if not file:
        return "In message.attachments, failed to find `patterns.arr` file"
    return file.read()


def seperate_flags_from_patterns(dirty_arr) -> Tuple[List[str], List[str]]:
    flags = []
    patterns = []

    # [], []
    if not dirty_arr:
        return patterns, flags
    # Only flags start with "-"
    if dirty_arr[0].startswith("-"):
        return patterns, dirty_arr
    # Find flag
    flag_ind = None
    for i in dirty_arr:
        if i.startswith("-"):
            flag_ind = dirty_arr.index(i)
            break

    if not flag_ind:
        return dirty_arr, flags
    else:
        return dirty_arr[:flag_ind], dirty_arr[flag_ind:]


def join(pat):
    return f"{pat[0]}:({pat[1]})->{pat[2]}"


def clean_patterns(dirty_arr: list) -> List[str]:
    if not dirty_arr:
        return dirty_arr
    # Command splits by " ", so rejoin
    # ["", "", "", ""]
    # "" "" "" ""
    # "..." "..." "..." "..."
    actual = " ".join(dirty_arr)
    gs = [join(i) for i in LUT_RE.findall(actual)]
    if " ".join(gs) == actual:
        return gs

    # "4:(... ... ...)->1" | 4:(... ... ...)->1
    if LUT_RE.fullmatch(act := actual.strip("\"")):
        return [act]

    # Now we assume node provided is a list
    try:
        node = literal_eval(actual)

        if type(node) == list:
            if all(LUT_RE.fullmatch(i.strip("\"")) for i in node):
                return [i.strip("\"") for i in node]
    except Exception:
        pass
    return "Cannot load provided pattern"


async def custom(ctx: Context, source: str = None, *flags_or_patterns) -> Any:
    patterns, flags = await ctx.bot.loop.run_in_executor(None, seperate_flags_from_patterns, flags_or_patterns)
    patterns = clean_patterns(patterns)

    if type(patterns) != list:
        return await ctx.reply(content=patterns)
    if not patterns:
        pos = read_from_file(ctx)
        if isinstance(pos, str):
            return await ctx.reply(content=pos)
        patterns = (await pos).decode(errors="ignore").split(" ")
        patterns = clean_patterns(patterns)

    prsed = vars(await ctx.bot.loop.run_in_executor(None, parser.parse_args, flags))

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

    if filters := prsed["filters"] and prsed["f_group"] == "BEFORE":
        prsed["filters"] = filters[:5]
        stream, opts, status = combine(stream, **prsed)

    def applyMorph():
        # morph
        morph = gen_custom_morph(patterns)
        return apply_morph(stream, morph, **prsed)
    
    try:
        exportable, *opts = await ctx.bot.loop.run_in_executor(None, applyMorph)
    except Exception as e:
        return await ctx.reply(content=e)

    if filters := prsed["filters"] and prsed["f_group"] == "AFTER":
        prsed["filters"] = filters[:5]
        exportable, opts, status = combine(exportable, **prsed)

    kwds = {"pot": prsed["form"], "sf": prsed["skip"]}
    if opts:
        kwds.update({"duration": opts[0], "loop": opts[1]})

    file = to_file(exportable, prsed["export-type"], **kwds)
    getattr(stream, "close", lambda: "")()

    if file.is_image:
        embed = Embed(title="Morphed (CUSTOM) image", colour=Colour.red())
        embed.add_field(name="Pattern", value=f"```\n{patterns}```")
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
        m = await ctx.reply(content="Morphed (CUSTOM) image data []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = custom
COMMAND_NAME = "custom"
COMMAND_DESCRIPTION = "Morph an image using a custom pattern"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = f"""
{COMMAND_DESCRIPTION}

Note:
  You can attach a file named "patterns.arr" which contains your patterns.
  Check usage for formatting

PATTERN-FORMAT:
  OP:(PATTERN)->RESULT

CHOICES:
  OP:
    4 - 4 Way Rotation
    N - Negate
    1 - Dummy OP [Does nothing]
    M - Mirroring
  PATTERN:
    . or X - Ignore
    1 - Pixel is ON
    0 - Pixel is OFF
  RESULT:
    0 - Pixel is OFF
    1 - Pixel is ON
"""
COMMAND_USAGE = """
ct!morph custom [src...] [patterns...]
ct!morph custom [src...] [patterns...] [--flags]?

Example:
  ct!morph custom bT_CV 4:(.10 01. ...)->1
  ct!morph custom bT_CV 4:(.10 01. ...)->1 M:(.10 01. ...)->0
  ct!morph custom bT_CV ["4:(.10 01. ...)->1", "N:(.10 00. .1.)->0"]
  ct!morph custom bT_CV "4:(.10 01. ...)->1" --cache
"""
