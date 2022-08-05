## Refresh file trees :D
import discord
from discord.ext.commands import Context, is_owner
import pprint


@is_owner()
async def main(ctx: Context):
    from core.tree import refresh, TREE

    msg = await ctx.reply(content="Refreshing trees")
    ctx.bot.commands.clear()

    # Refresh functions
    await ctx.bot.loop.run_in_executor(None, refresh)

    embed = discord.Embed(title="Trees affected", colour=discord.Colour.red())
    embed.description = "```\n" + pprint.pformat(TREE, indent=4) + "\n```"

    return await msg.edit(content="Trees refreshed", embed=embed)


COMMAND_CALLBACK = main
COMMAND_NAME = "refresh"
COMMAND_DESCRIPTION = "Refresh all command trees"
COMMAND_HELP = COMMAND_DESCRIPTION
COMMAND_BRIEF = COMMAND_DESCRIPTION
COMMAND_ALIASES = ["ref", "reb"]
COMMAND_USAGE = "ct!refresh"
