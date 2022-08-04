import sys
import pprint
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from src.core.bot import bT_CV
from src.core import tree as tr

inst = bT_CV()      # Not running so no token required
tr.setInstance(inst)
tr.loadTree()

print("Generated tree:\n")
pprint.pprint(tr.TREE)
print("\n", "-"*50)
