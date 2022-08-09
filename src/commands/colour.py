from discord import Embed, File
from discord.ext.commands import Context
from PIL import Image
from io import BytesIO
import re

from pydantic.color import Color, ColorError

RGB_TUP = re.compile(r"^\( *([0-9]) *, *([0-9]) *, *([0-9]) *\) *$")
RGBA_TUP = re.compile(r"^\( *([0-9]) *, *([0-9]) *, *([0-9]), *([0-9]) *\) *$")


def cleanup(string) -> str:
    if match := RGBA_TUP.match(string):
        return f"rgba({', '.join(match.groups[1:])})"
    if match := RGB_TUP.match(string):
        return f"rgb({', '.join(match.groups[1:])})"
    return string

 
async def colour(ctx: Context, *colour: str):
    if not colour:
        return await ctx.reply(content="No colour provided")

    col = " ".join(colour)
    try:
        col_cls = Color(cleanup(col))
    except ColorError as e:
        return await ctx.reply(content=e)

    with BytesIO() as stream:
        val = int("0x" + col_cls.as_hex()[1:], 16)
        mode = "RGB" if not col_cls._rgba.alpha else "RGBA"
        base = Image.new(mode=mode, size=(900, 900), color=val)
        base.save(stream, "PNG")
        stream.seek(0)

        em = Embed(title=f"Generated colour ({col_cls.original()})", colour=val)
        em.set_image(url="attachment://result.png")
        return await ctx.reply(embed=em, file=File(stream, "result.png"))


COMMAND_CALLBACK = colour
COMMAND_NAME = "colour"
COMMAND_DESCRIPTION = "Generate a colour"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = f"""\
{COMMAND_DESCRIPTION}

Colour formats:
  as_name: "Black", "red", "pink", ...
  hex_value: "#FFFFFF", "0x000"
  RGB/RGBA tuples: rgb(r, g, b) rgba(r, g, b, a)
  HSL strings: "hsl(270, 60%, 70%)", "hsl(270, 60%, 70%, .5)"
"""
COMMAND_USAGE = f"""
ct![colour|color] [colour:string]
"""
COMMAND_ALIASES = ["color"]
