# File tree command loader sys
import os
from discord.ext.commands import Bot, Command
import importlib


INSTANCE: Bot = None
COMMANDS_DIRECTORY: str = os.path.abspath("./src/commands")
TREE: list = list()
COMMANDS: list = list()

COMMAND_ATTRS = {
    "callback",
    "name",
    "enabled",
    "help",
    "brief",
    "usage",
    "rest_is_raw",
    "aliases",
    "extras",
    "aliases",
    "description",
    "hidden",
    "checks",
    "cooldown",
    "max_concurrency",
    "require_var_positional",
    "ignore_extra",
    "cooldown_after_parsing",
    "cog",

}


def setInstance(bT_CV_Inst: Bot) -> None:
    global INSTANCE

    INSTANCE = bT_CV_Inst


def treeGrouper(path: str) -> list:
    files = []

    for file in os.listdir(path):
        PA = COMMANDS_DIRECTORY + "/" + file
        if os.path.isdir(PA):
            n_files = treeGrouper(PA)

            if not n_files:
                continue

            files.append([file, n_files])
        else:
            if not file.endswith(".py"):
                continue
            files.append(file)
    return files


def treeInitG() -> list:
    commands = []
    BASE_LEVEL_DIR = os.path.dirname(COMMANDS_DIRECTORY)

    for file in TREE:
        if isinstance(file, list):



def loadTree() -> None:
    global TREE

    TREE = treeGrouper(COMMANDS_DIRECTORY)


def initTree():
    global COMMANDS

    COMMANDS = treeInitG()


def addCommands():
    pass
