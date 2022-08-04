# Command tree system
Instead of using the traditional method of creating commands,
bT_CV utilises a tree type system.

## Function decl
Function declarations will remain as normal,
```py
async def myFunction(ctx, ..., *, [...]) -> ...:
    ...
```

For fetching your desired command function.
The file must have set the ``COMMAND_CALLBACK`` attr.

If you dont want your function declaration being used as your command name.
Modify all command registration attributes by declaring them as:
```py
# COMMAND_[ATTR] = [ATTR-VALUE]
COMMAND_NAME = "..."
```

or, if your lazy like most of us:
```py
COMMAND_ATTRS = {
    # [ATTR]: [ATTR-VALUE]
    "name": "..."
}
```

### Function checks [Cooldowns, before-invokes, etc...]
These all work the same way as before!

```py
@commands.cooldown(..., [...])
async def foo(ctx: Context, ..., *, [...]):
    ...
```

## Cogs
```
src
| commands
  | cogs
    | cog1.py   # Cog in here
  | ref.py      # Add command to cog1 by using
                # COMMAND_LINK_COG = [COG-CLASS]
```

### Cog func definition
```py
async def foo([self]?, ctx: Context, ..., *, [...]):
    ...
```
* The self parameter at the start may or may not be included
    - If not included : Command added after cog initialised
    - If set : Command added to cog like it was placed in it [Pre-intialisation]
* Self parameter is essentially an instance of the cog class!

#### Example

```py
# import cog
from src.commands.cogs.cog1 import Cog1
import ...

# Define function
async def cogExample(self: Cog1, ctx: Context, [...]) -> Any:
    ...

# Declare command constants
COMMAND_CALLBACK = cogExample
COMMAND_NAME = "cogExample"
COMMAND_LINK_COG = "Cog1"
```

## Function Registering
Now with all tree systems,
we use directories and files to name/find commands.

### Example Dir
```
src
| commands
  | foo.py          [COMMAND_NAME="foo"]
  | baz.py          [COMMAND_NAME="baz"]
  | bar
    | qux.py        [COMMAND_NAME="qux"]
    | grouper.py    [COMMAND_NAME="bar"]
  | no_source
    | ...           # This group is ignore
  | no_decl.py      # This file is ignored - no attrs set
```
bT will first iterate through commands gathering all files,
any dirs will be iterated separately.

The special file ``grouper.py`` will provide a basic callback for the groups parent.
so ``grouper>>COMMAND_NAME`` will call the ``grouper>>COMMAND_CALLBACK`` for whenever the
bar command is used as ``bar`` but not when called as ``bar qux``.
Then ``bar>>qux>>COMMAND_CALLBACK`` is called instead.

**Note:** To ignore files, either dont set ``COMMAND_CALLBACK`` or set ``IGNORE`` as a true value.
