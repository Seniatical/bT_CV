from typing import Any
from discord import Embed, Colour
from discord.ext.commands import Context

from core.com_par import parser
from api.combine import combine
from api.loader import to_stream
from api.export import to_file, gen_cache_id
from api.morph import erosion4_morph

from binascii import Error
from api.loader import SourceNotFound, FileTooLarge


async def erosion4(ctx: Context, source: str = None, *flags) -> Any:
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
        return erosion4_morph(stream, **prsed)

    exportable, *opts = await ctx.bot.loop.run_in_executor(None, applyMorph)

    if filters := prsed["filters"] and prsed["f_group"] == "AFTER":
        prsed["filters"] = filters[:5]
        exportable, opts, status = combine(exportable, **prsed)

    kwds = {"pot": prsed["form"], "sf": prsed["skip"]}
    if opts:
        kwds.update({"duration": opts[0], "loop": opts[1]})

    file = to_file(exportable, prsed["export-type"], **kwds)
    getattr(stream, "close", lambda: "")()

    if file.is_image:
        embed = Embed(title="Morphed (EROSION4) image", colour=Colour.red())
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
        m = await ctx.reply(content="Morphed (EROSION4) image data []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = erosion4
COMMAND_NAME = "erosion4"
COMMAND_USAGE = """
ct!morph erosion4 [src...]?
ct!morph erosion4 [src...]? [--flags]
"""
COMMAND_DESCRIPTION = "Morph an image using the erosion4 option!"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = COMMAND_DESCRIPTION

