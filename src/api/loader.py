# Load file and return an output stream
import re
from io import BytesIO, SEEK_END
from discord.ext.commands import (
    Context,
    MemberConverter,
    EmojiConverter,
    MemberNotFound,
    EmojiNotFound
)
from base64 import b64decode
from ast import literal_eval
from PIL import Image

URL_MA = re.compile(
    r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)
COMMAND_MA = re.compile(
    r"^ct! *([a-zA-Z]+) *([a-zA-Z0-9\-]+(?: *))*"
)
MEM_CONV = MemberConverter()
EM_CONV = EmojiConverter()
MAX_SIZE = 5e+6


class FileTooLarge(Exception):
    ...


class SourceNotFound(Exception):
    ...


def get_asset_url(asset):
    print(asset.BASE + asset._url)
    return asset.BASE + asset._url


class Source:
    def __init__(self, source):
        self.src = source

    @property
    def content(self):
        if isinstance(self.src, str):
            return self.src or ""
        return self.src.content or ""

    @property
    def embeds(self):
        return getattr(self.src, "embeds", None)

    @property
    def attachments(self):
        return getattr(self.src, "attachments", None)


async def to_stream(ctx: Context, **kwds) -> BytesIO:
    """
    SUPPORTED_TYPES:
        - Plain image/... content type
        - Base64 encoded image
        - Array - [[], ...]
        - HTML - y not
    """

    src = kwds.pop("url", None) or await find_source(ctx, **kwds)
    if isinstance(src, BytesIO):
        return src

    assert URL_MA.match(src) is not None

    async with ctx.bot.session.get(src) as resp:
        body = resp._body or await resp.read()

        if resp.headers['Content-Type'].startswith("image/"):
            s = BytesIO(body)
        elif arr := literal_eval(body.decode("utf-8")) \
                    and body.startswith(b"[") \
                    and body.endswith(b"]"):
            s = BytesIO()
            pi = Image.fromarray(arr)

            pi.save(s, pi.format)
            pi.close()
        elif len(body) % 4 == 0:
            s = BytesIO(b64decode(body, validate=True))
        else:
            raise ValueError("...")
        size = s.seek(0, SEEK_END)

        if size > MAX_SIZE:
            raise FileTooLarge(f"File size cannot be larger then `{MAX_SIZE}`, got {size}")
        s.seek(0)

        return s


async def find_source(ctx: Context, arg: str, sec: bool = False, source_select: int = -1) -> str:
    source = Source(arg or ctx.message)

    if not hasattr(source, "content"):
        setattr(source, "content", source)

    if ctx.message.reference and getattr(ctx.message.reference, "resolved", False) and not sec:
        source = Source(arg or ctx.message.reference.resolved)

    if match := URL_MA.match(source.content):
        return match.group(0)
    if source.embeds:
        em = source.embeds[source_select]
        if em.image:        return em.image.url
        if em.thumbnail:    return em.thumbnail.url
        if em.author:       return em.author.url
        if em.footer:       return em.footer.icon_url
    if source.attachments:
        return source.attachments[source_select].url

    try:
        if member := await MEM_CONV.convert(ctx, source.content):
            if (ur := member.avatar._url).startswith("https"):
                return ur
            return get_asset_url(member.avatar_url)
    except MemberNotFound:
        pass

    try:
        if emoji := await EM_CONV.convert(ctx, source.content):
            uri = emoji.url
            if not isinstance(uri, str):
                return get_asset_url(uri)
            return uri
    except EmojiNotFound:
        pass

    if source.content.lower() == "guild":
        return get_asset_url(ctx.guild.icon_url if ctx.guild.icon else ctx.author.avatar_url)
    if source.content.lower() == "me":
        return get_asset_url(ctx.author.avatar_url)
    if source.content.lower() == "banner":
        return get_asset_url(ctx.guild.banner_url if ctx.guild.banner else ctx.author.avatar_url)
    if source.content.lower() == "sample":
        return "https://media1.tenor.com/images/505e4a6c227a15e7d3a813354d3229f4/tenor.gif?itemid=4520105"

    if cache := ctx.bot.runtime_cache["IMAGES"].get(source.content):
        if cache["priv"] and ctx.author.id == cache["user"]:
            return cache["uri"]
        elif not cache["priv"]:
            return cache["uri"]

    ## Now we check for a command re-run
    try:
        cmd, *args = source[3:].content.split(" ")

        if command := ctx.bot.all_commands.get(cmd.lower()):
            res = command(ctx, *args, return_raw=True)
            # We have an actual source file/stream
            # Returning this should have no problem internally
            return res

    except Exception:
        pass

    if sec:
        raise SourceNotFound()
    ctx.message.content = arg
    return await find_source(ctx, "", True, source_select)
