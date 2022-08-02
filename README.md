# bT_CV

A bot to complete many image related things.
Made for the **2022 Server Bot Jam**.

## Features
* Fast, rapid image editing with many filters, templates and more!
* Support for many file types including GIFs
* Multiple output options, including arrays, HTML and base64
* Provides basic control with a simple language to utilise user templates and more
* Load files from many sources!
* Has some more, just too lazy.

[Invite Me Here](https://discord.com/api/oauth2/authorize?client_id=1003748391353851954&permissions=274878024768&redirect_uri=https%3A%2F%2Fgithub.com%2FSeniatical%2FbT_CV&response_type=code&scope=bot)

# Team
* Senatical "[@Seniatcal](https://github.com/Seniatical)"

# Running bot locally
```sh
git clone https://github.com/Seniatical/bT_CV
cd bT_CV
make dependencies
make setToken ...
make run

#Bot is now running!
```

## Changing startup checks
In each of the startup check files,
there are constants which can be changed inorder to modify the checks.

### Files:
* core/check_database.py
* core/check_dependencies.py
* core/check_file_stores.py
* core/make_logs.py
