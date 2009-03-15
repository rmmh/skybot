import hashlib

#command
def md5(bot, input):
    return hashlib.md5(input.inp).hexdigest()

#command
def sha1(bot, input):
    return hashlib.sha1(input.inp).hexdigest()

#command
def hash(bot, input):
    return ', '.join(x + ": " + getattr(hashlib, x)(input.inp).hexdigest()
            for x in 'md5 sha1 sha256'.split())
