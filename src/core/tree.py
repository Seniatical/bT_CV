# File tree command loader sys
import os
from discord.ext.commands import Bot, Command, Group, Cog
import importlib.util
import logging
from typing import Optional, Union, List, Tuple

INSTANCE: Bot                           = None
COG_DIR_NAME: str                       = "cogs"
COMMANDS_DIRECTORY: str                 = os.path.abspath("./src/commands")
TREE: List[Union[List[str], str]]       = list()
COMMANDS: List[Union[Command, Group]]   = list()
COGS: List[Cog]                         = list()
S_LOG: logging.Logger                   = logging.getLogger("bt_status")

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
    "invoke_without_command"
}


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


def sortCogs(path: str) -> List[Cog]:
    # Returns a list of cog classes
    files = [i for i in os.listdir(path) if i.endswith(".py")]
    cwd = os.getcwd()
    relative_to_path = path[len(cwd):-3].replace("/", ".")
    cogs = []

    for file in files:
        relative_to_file = relative_to_path + "." + file[:-3]
        lib = importlib.import_module(relative_to_file)

        if not (cog_name := getattr(lib, "COG_NAME", None)):
            S_LOG.warning("Failed to add cog \"%s\". Unable to locate cog class", relative_to_file)
            continue
        cog = getattr(lib, cog_name, None)
        if not cog:
            S_LOG.warning("Incorrect reference to cog class, %s", relative_to_file)
            continue
        cogs.append(cog)
    return cogs


def source_to_command(path: str, *, asG: bool = False) -> Optional[Union[Command, Group]]:
    # returns a parsed command object from a file
    assert os.path.exists(path)

    if os.path.isdir(path):
        return folder_to_commands(path)

    cwd = os.getcwd()
    relative_to_file = path[len(cwd) + 1:-3].replace("/", ".")

    try:
        lib = importlib.import_module(relative_to_file)
    except ModuleNotFoundError:
        # Lib is 1 dir forwards
        lib = importlib.import_module(relative_to_file[4:])

    importlib.reload(lib)

    if getattr(lib, "IGNORE", False):
        return None
    elif not getattr(lib, "COMMAND_CALLBACK", None):
        S_LOG.warning("No callback set for \"%s\", skipping command", relative_to_file)
        return None

    opts = dict()
    for opt in COMMAND_ATTRS:
        try:
            opts[opt] = getattr(lib, f"COMMAND_{opt.upper()}")
        except AttributeError:
            continue

    callback = opts.pop("callback")

    if asG:
        command = Group(callback, **opts)
    else:
        command = Command(callback, **opts)

    if (link_to := getattr(lib, "COMMAND_LINK_COG", None)):
        command.COG_LINK = link_to

    return command


def folder_to_commands(path: str) -> Optional[Union[Group, List[Union[Group, Command]]]]:
    assert os.path.isdir(path)

    files = os.listdir(path)
    if "grouper.py" not in files:
        return [source_to_command(path + "/" + i) for i in files if i.endswith(".py")]
    group_base = source_to_command(path + "/grouper.py", asG=True)
    
    if not group_base:
        S_LOG.warning("Group command for \"%s\" has been skipped - Invalid grouper file", path)
        S_LOG.info("Skipped files from %s: %s", path, files)
        return None

    files.pop(files.index("grouper.py", 0, -1))
    
    for file in files:
        if isinstance(file, list):
            cm = folder_to_commands(path + "/" + file[0])
        else:
            cm = source_to_command(path + "/" + file)
        if not cm:
            continue

        group_base.add_command(cm)
    return group_base


def link_command_to_cog(command, cog_iden) -> None:
    if isinstance(cog_iden, str):
        cog = None
        for cog in COGS:
            if cog_iden == getattr(cog, "__cog_name__", ""):
                cog = cog
                break
    else:
        cog = cog_iden

    if not cog:
        raise ValueError("Unable to find cog with name \"" + cog_iden + "\"")

    if isinstance(cog, Cog):
        ## Initialised
        cog.__cog_commands__ = cog.__cog_commands__ + (command, )
    elif cog.__class__ == type:
        # Command(name="Bar", callback=bar)
        # Cog.bar = Command(name="Bar", ...)
        setattr(cog, command.callback.__name__, command)
    else:
        raise TypeError("Invalid cog type provided")


def treeInitG() -> Tuple[List[Union[Group, Command]], List[Cog]]:
    commands = []
    cogs = []

    for file in TREE:
        if isinstance(file, list):
            _dir, files = file
            if _dir == COG_DIR_NAME:
               cogs = sortCogs(COMMANDS_DIRECTORY + "/" + _dir)
            else:
                group = folder_to_commands(COMMANDS_DIRECTORY + "/" + _dir)
                if not group:
                    continue

                if isinstance(group, list):
                    commands.extend(filter(lambda x: x is not None, group))
                else:
                    commands.append(group)
        else:
            cmd = source_to_command(COMMANDS_DIRECTORY + "/" + file)
            if not cmd:
                continue
            commands.append(cmd)

    return commands, cogs


def setInstance(bT_CV_Inst: Bot) -> None:
    global INSTANCE

    INSTANCE = bT_CV_Inst


def loadTree() -> None:
    global TREE

    TREE = treeGrouper(COMMANDS_DIRECTORY)


def initTree() -> None:
    global COMMANDS, COGS

    COMMANDS, COGS = treeInitG()


def addCogs(override: bool = False):
    for cog in COGS:
        INSTANCE.add_cog(cog, override=override)


def addCommands():
    for command in COMMANDS:
        if link := getattr(command, "COG_LINK", ""):
            link_command_to_cog(link)
        else:
            INSTANCE.add_command(command)


def setup(cog_override: bool = False):
    addCogs(cog_override)
    addCommands()


def init(
        instance: Bot,
        *,
        cog_override: bool = False
):
    setInstance(instance)
    loadTree()
    initTree()

    setup(cog_override)


def refresh(*opts):
    global INSTANCE, TREE, COMMANDS, COGS
    inst = None
    ovr = False

    if opts:
        inst = opts[0]
        assert isinstance(inst, Bot)
        try:
            ovr = bool(opts[1])
        except IndexError:
            pass

    INSTANCE = inst or INSTANCE
    TREE = list()
    COMMANDS = list()
    COGS = list()

    # Unload EVERYTHING
    INSTANCE._BotBase__cogs = dict()
    INSTANCE.all_commands = {"help": INSTANCE.all_commands["help"]}

    # Refresh commands and tree
    loadTree()
    initTree()

    setup(cog_override=bool(ovr))
