from discord.ext.commands import (
    BucketType,
    cooldown,
    Context,
    Group
)
from typing import Any


@cooldown(5, 60, BucketType.member)
async def main(ctx: Context) -> Any:
    command: Group = ctx.command
    content = "[Filter command] | {} filters".format(len(command.commands))
    content += "\n```\n"
    content += "\n".join("> " + sub_cmd.name for sub_cmd in command.commands)
    content += "\n```\n"

    return await ctx.reply(content=content)


COMMAND_CALLBACK = main
COMMAND_NAME = "filter"
COMMAND_DESCRIPTION = "Applies an effect on to your desired image"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = f"""\
{COMMAND_DESCRIPTION}

Flags:
  -sS --source-select [integer] default=-1
  -E --export [string] [image | base64 | array] default=image
  -iF --image-format [str] [PNG | JPG | GIF | JPEG] default=AUTO
  -C --cache [FLAG] default=False
  -fC --from-cache [str (cache_id)] default=None
  -nA --no-animate [FLAG] default=False
  -F --frame [int] default=0
"""
COMMAND_USAGE = """\n
ct![filter|effect] [effect] [src]? [--options, ...]?
"""
COMMAND_ALIASES = ["effect"]
COMMAND_INVOKE_WITHOUT_COMMAND = True
