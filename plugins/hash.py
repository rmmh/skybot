import hashlib

from util import hook


@hook.command
def md5(inp):
    return hashlib.md5(inp).hexdigest()


@hook.command
def sha1(inp):
    return hashlib.sha1(inp).hexdigest()


@hook.command
def hash(inp):
    ".hash <text> -- returns hashes of <text>"
    return ', '.join(x + ": " + getattr(hashlib, x)(inp).hexdigest()
            for x in 'md5 sha1 sha256'.split())
