import discord
from discord.ext.commands import Bot
import os
import dotenv
import logging

dotenv.load_dotenv()
S_LOG = logging.getLogger("bt_status")


class bT_CV(Bot):
    def __init__(self, **kwds):
        self.TOKEN_FILE = "./bot.token"
        self.kwds = {
            "command_prefix": "ct!",
            "case_insenstive": True,
            "intents": discord.Intents.all(),
            "status": discord.Status.online,
            "activity": discord.Activity(
                type=discord.ActivityType.competing,
                name="All these other bots"
            ),
            **kwds
        }

        super().__init__(**self.kwds)
        
    def run(self, bot_token: str = None, *, reconnect=True):
        S_LOG.debug("Preparing to run %s", self.__class__.__name__)
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE) as fp:
                token = fp.read(-1)
        else:
            token = os.getenv("BOT_TOKEN")
        token = bot_token or token

        if not token:
            S_LOG.critical("No token provided to run %s", self.__class__.__name__)
            raise ValueError("No token provided to run {}".format(self.__class__.__name__))
        S_LOG.debug("Running %s", self.__class__.__name__)

        super().run(token, reconnect=True)
