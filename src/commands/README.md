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
# COMMAND_[ATTR-HERE] = "..."
COMMAND_NAME = "..."
```

or, if your lazy like most of us:
```py
COMMAND_ATTRS = {
    # [ATTR]: [ATTR-VALUE]
    "name": "..."
}
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
```
bT will first iterate through commands gathering all files,
any dirs will be iterated separately.

The special file ``grouper.py`` will provide a basic callback for the groups parent.
so ``grouper>>COMMAND_NAME`` will call the ``grouper>>COMMAND_CALLBACK`` for whenever the
bar command is used as ``bar`` but not when called as ``bar qux``
