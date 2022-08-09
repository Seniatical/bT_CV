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
    content = "[Enhance commands] | {} Tot".format(len(command.commands))
    content += "\n```\n"
    content += "\n".join("> " + sub_cmd.name for sub_cmd in command.commands)
    content += "\n```\n"

    return await ctx.reply(content=content)


COMMAND_CALLBACK = main
COMMAND_NAME = "enhance"
COMMAND_DESCRIPTION = "Change a factor on an image to enhance it"
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
"""
COMMAND_USAGE = """
ct!enchance [mode] [factor] [--flags]?
"""
COMMAND_INVOKE_WITHOUT_COMMAND = True

