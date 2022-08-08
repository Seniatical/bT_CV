from PIL import Image
from discord import Embed, Colour
from discord.ext.commands import Context
from argparse import ArgumentParser
from typing import Any
from api.export import to_file
from api.combine import combine


# Parser for image generators
partial_parser = ArgumentParser()

partial_parser.add_argument(
    "-E", "--export",
    type=str, choices=["image", "base64", "array"],
    default="image",
    dest="export-type"
)

partial_parser.add_argument(
    "-iF", "--image-format", type=str, dest="form",
    choices=["GIF", "PNG", "JPEG", "JPG"],
    default="AUTO"
)

partial_parser.add_argument(
    "-C", "--cache", action="store_true", dest="cache", default=False
)

partial_parser.add_argument(
    "-Cp", "--cache-protect", action="store_true", dest="cache-protect", default=False
)

partial_parser.add_argument(
    "-f", "--filter", action="append", type=str, dest="filters", default=[]
)

## END PARSER


async def mandelbrot(ctx: Context,
                     width: int = 500, height: int = 500,
                     x0: int = 0, y0: int = 500,
                     x1: int = 500, y1: int = 500,
                     *flags
                     ) -> Any:
    prsed = vars(await ctx.bot.loop.run_in_executor(None, partial_parser.parse_args, flags))

    # MAX = 1000
    width = width if width < 1000 else 1000
    height = height if height < 1000 else 1000

    def generate():
        res = Image.effect_mandelbrot(
            (width, height),
            (x0, y0, x1, y1),
            100
        )

        if prsed["filters"]:
            return combine(res, prsed["filters"][:5], **prsed)
        return res

    maybe_exportable = await ctx.bot.loop.run_in_executor(None, generate)
    file = to_file(maybe_exportable,
                   prsed["export-type"],
                   pot=prsed["form"]
                   )

    if file.is_image:
        embed = Embed(title="Mandelbrot generated image", colour=Colour.red())
        embed.set_image(url=f"attachment://{file.filename}")
        m = await ctx.reply(embed=embed, file=file)
    else:
        m = await ctx.reply(content="Mandelbrot generated image []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = mandelbrot
COMMAND_NAME = "mandelbrot"
COMMAND_USAGE = """
ct!generate mandelbrot [width,height:int=500]? [x0,y0,x1,y1:int]?
                        ^^^^^^^^^^^^^^^^^^^^
                              MAX=1000
"""
