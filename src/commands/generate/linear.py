from PIL import Image
from discord import Embed, Colour
from discord.ext.commands import Context
from typing import Any
from api.export import to_file
from .mandelbrot import partial_parser


async def linear_gradient(ctx: Context,
                          *flags
                          ) -> Any:
    prsed = vars(await ctx.bot.loop.run_in_executor(None, partial_parser.parse_args, flags))

    def generate():
        return Image.linear_gradient("L")

    maybe_exportable = await ctx.bot.loop.run_in_executor(None, generate)
    file = to_file(maybe_exportable,
                   prsed["export-type"],
                   pot=prsed["form"]
                   )

    if file.is_image:
        embed = Embed(title="Linear gradient generated image", colour=Colour.red())
        embed.set_image(url=f"attachment://{file.filename}")
        m = await ctx.reply(embed=embed, file=file)
    else:
        m = await ctx.reply(content="Linear gradient generated image []".format(file.export_as), file=file)

    if prsed["cache"]:
        attach = m.embeds[0].image.url
        cache_item = {(_id := gen_cache_id()): {"uri": attach, "priv": prsed["cache-protect"], "user": ctx.author.id}}
        ctx.bot.runtime_cache["IMAGES"].update(cache_item)
        content = m.content + "\n**CacheID:** " + _id

        return await m.edit(content=content)


COMMAND_CALLBACK = linear_gradient
COMMAND_NAME = "linear_gradient"
COMMAND_USAGE = """
ct!generate linear_gradient
"""
COMMAND_ALIASES = ["lg", "l_gradient", "lin_grad", "linear_grad"]
