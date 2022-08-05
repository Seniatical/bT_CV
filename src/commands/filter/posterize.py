import discord

from typing import Any
from discord.ext import commands
from api.loader import to_stream, FileTooLarge, SourceNotFound
from api.export import to_file, gen_cache_id
from api.effects import posterize as F
from core.com_par import parser
from binascii import Error


async def posterize(ctx: commands.Context, source: str = None, bits: int = 8, *flags, **priv) -> Any:
    prsed = vars(await ctx.bot.loop.run_in_executor(None, parser.parse_args, flags))
    if bits > 8:
        bits = 8
    elif bits < 1:
        bits = 1

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

    def filter():
        return F(stream, bits, animate=prsed["animate"], frame=prsed["frame"])

    exportable, *opts = await ctx.bot.loop.run_in_executor(None, filter)

    kwds = {"pot": prsed["form"]}
    if opts:
        kwds.update({"duration": opts[0], "loop": opts[1]})

    if priv.get("return_raw"):
        return exportable

    file = to_file(exportable, prsed["export-type"], **kwds)
    stream.close()

    if file.is_image:
        embed = discord.Embed(title="Posterized image", colour=discord.Colour.red())
        embed.set_image(url=f"attachment://{file.filename}")
        m = await ctx.reply(embed=embed, file=file)
    else:
        m = await ctx.reply(content="Posterized image data []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = posterize
COMMAND_NAME = "posterize"
COMMAND_USAGE = """\n
ct!posterize [src...]? [bits:int]
ct!posterize [src...]? [bits:int] [--flags]
"""
COMMAND_DESCRIPTION = "Posterize an image!"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = COMMAND_DESCRIPTION
