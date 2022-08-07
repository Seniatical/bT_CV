import sys
import pprint
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from src.core.bot import bT_CV
from src.core import tree as tr

inst = bT_CV()      # Not running so no token required
tr.setInstance(inst)

## Test file finder
tr.loadTree()

print("Generated tree:\n")
pprint.pprint(tr.TREE)
print("\n", "-"*50)

## Test loaders
tr.initTree()

print("\n", "-"*50)
print("Cogs located")
print(tr.COGS)
print("\n", "-"*50)

print("\n", "-"*50)
print("Commands loaded")
print(tr.COMMANDS)
print("\n", "-"*50)

## Add to bot
BEF_CMD = inst.commands
BEF_COGS = inst.cogs
tr.setup()

print("\n", "-"*50)
print("Loading commands to bot")
print("BEFORE COMMANDS:", BEF_CMD)
print("BEFORE COGS:", BEF_COGS)
print("\n", "-"*50)

print("AFTER COMMANDS:", inst.commands)
print("AFTER COGS:", inst.cogs)
