from PIL import Image
from discord import Embed, Colour
from discord.ext.commands import Context
from typing import Any
from api.export import to_file
from .mandelbrot import partial_parser


async def gaussian_noise(ctx: Context,
                         sigma: int,
                         width: int = 500, height: int = 500,
                         *flags
                         ) -> Any:
    prsed = vars(await ctx.bot.loop.run_in_executor(None, partial_parser.parse_args, flags))

    # MAX = 1000
    width = width if width < 1000 else 1000
    height = height if height < 1000 else 1000

    def generate():
        return Image.effect_noise(
            (width, height),
            sigma
        )

    maybe_exportable = await ctx.bot.loop.run_in_executor(None, generate)
    file = to_file(maybe_exportable,
                   prsed["export-type"],
                   pot=prsed["form"]
                   )

    if file.is_image:
        embed = Embed(title="Gaussian noise generated image", colour=Colour.red())
        embed.set_image(url=f"attachment://{file.filename}")
        m = await ctx.reply(embed=embed, file=file)
    else:
        m = await ctx.reply(content="Gaussian noise generated image []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = gaussian_noise
COMMAND_NAME = "gaussian_noise"
COMMAND_USAGE = """
ct!generate gaussian_noise [width,height:int=500]? [x0,y0,x1,y1:int]?
                            ^^^^^^^^^^^^^^^^^^^^
                                  MAX=1000
"""
COMMAND_ALIASES = ["gn", "noise"]
