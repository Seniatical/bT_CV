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
    content = "[Generate commands] | {} Tot".format(len(command.commands))
    content += "\n```\n"
    content += "\n".join("> " + sub_cmd.name for sub_cmd in command.commands)
    content += "\n```\n"

    return await ctx.reply(content=content)


COMMAND_CALLBACK = main
COMMAND_NAME = "generate"
COMMAND_INVOKE_WITHOUT_COMMAND = True
COMMAND_DESCRIPTION = "Generate random images using pre-made effects"
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_HELP = f"""\
{COMMAND_DESCRIPTION}

Flags:
  -E --export [string] [image | base64 | array] default=image
  -iF --image-format [string] [PNG | JPG | GIF | JPEG] default=AUTO
  -C --cache [FLAG] default=False
  -cP --cache-protect [FLAG] default=False
  -f --filter [string] [stack=5] default=[]
"""
COMMAND_ALIASES = ["gen"]
