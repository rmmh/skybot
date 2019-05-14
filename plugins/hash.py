import hashlib

from util import hook


@hook.command('md5')
def hash_md5(inp):
    return hashlib.md5(inp.encode('utf-8')).hexdigest()


@hook.command('sha1')
def hash_sha1(inp):
    return hashlib.sha1(inp.encode('utf-8')).hexdigest()

@hook.command('sha256')
def hash_sha256(inp):
    return hashlib.sha256(inp.encode('utf-8')).hexdigest()

@hook.command
def hash(inp):
    """.hash <text> -- returns hashes of <text>"""

    hashes = [
        (x, hashlib.__dict__[x](inp.encode('utf-8')).hexdigest())
        for x in 'md5 sha1 sha256'.split()
    ]

    return ', '.join("%s: %s" % i for i in hashes)
