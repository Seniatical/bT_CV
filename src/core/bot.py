import discord
from discord.ext import commands
import os
import dotenv
import logging
from inspect import Parameter
import aiohttp
from cv2 import error

from . import tree

dotenv.load_dotenv()
S_LOG = logging.getLogger("bt_status")
C_LOG = logging.getLogger("ct_commands")


class bT_CV(commands.Bot):
    def __init__(self, **kwds):
        self.TOKEN_FILE = "./bot.token"
        self.b_name = self.__class__.__name__
        self.session = None

        self.kwds = {
            "command_prefix": "ct!",
            "case_insensitive": True,
            "intents": discord.Intents.all(),
            "status": discord.Status.online,
            "activity": discord.Activity(
                type=discord.ActivityType.competing,
                name="the 2022 bot jam!"
            ),
            **kwds
        }
        self.runtime_cache = {
            "IMAGES": dict()
        }

        super().__init__(**self.kwds)

    async def on_command(self, ctx, *args, **kwds):
        auth = f"{ctx.author.name.encode(errors='ignore').decode()}"
        guild = f"{ctx.guild.name.encode(errors='ignore').decode()} [{ctx.guild.id}]"
        C_LOG.debug(f"{auth} used {ctx.command.name} in {guild}")

    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            c = exception.args[0]
            return await ctx.reply(content=c)

        elif isinstance(exception, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            prefix_ = "ct!"

            params = [ctx.command.clean_params[i] for i in ctx.command.clean_params]
            listed_message = ['```{}{} '.format(prefix_, ctx.command.name), '```']
            for param in params:
                if param.default == Parameter.empty:
                    listed_message.insert(-1, '<' + param.name + '> ')
                else:
                    listed_message.insert(-1, '[' + param.name + '={}] '.format(param.default))

            listed_message.insert(-1, '\n' + exception.args[0])

            missing = exception.param
            try:
                index = listed_message.index('<' + missing.name + '> ', 0)
            except ValueError:
                index = listed_message.index('[' + missing.name + '] ', 0)

            listed_message.insert(-2, '\n')
            for i in range(index):
                listed_message.insert(-2, (' ' * (len(listed_message[index - 1]) - 3)))
            listed_message.insert(-2, '^' * len('<' + missing.name + '>'))

            await ctx.reply(content=''.join(listed_message))

        elif isinstance(exception,
                        (commands.CommandOnCooldown, commands.MemberNotFound)
                        ):
            return await ctx.reply(content=exception.args[0])

        else:
            if og := getattr(exception, "original", None):
                if isinstance(og, error):
                    return await ctx.reply(content="An error occurred with your image\n```" + og.args[0] + "```")
            await ctx.reply(content="An error has occured!")
            raise exception

    async def on_connect(self):
        S_LOG.info("%s has connected, intialising commands", self.b_name)

        self.session = aiohttp.ClientSession()
        S_LOG.debug("Client session created")

        tree.setInstance(self)
        S_LOG.debug("Set instance")
        tree.loadTree()
        S_LOG.debug("Tree loaded")
        tree.initTree()
        S_LOG.debug("Commands have been sourced and cached")

        tree.setup()

        S_LOG.info("%s has loaded %s of %s commands", self.b_name, len(self.commands), len(tree.COMMANDS))
        
    def run(self, bot_token: str = None, *, reconnect=True):
        S_LOG.debug("Preparing to run %s", self.b_name)
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE) as fp:
                token = fp.read(-1)
        else:
            token = os.getenv("BOT_TOKEN")
        token = bot_token or token

        if not token:
            S_LOG.critical("No token provided to run %s", self.b_name)
            raise ValueError("No token provided to run {}".format(self.b_name))
        S_LOG.debug("Running %s", self.b_name)

        super().run(token, reconnect=reconnect)
