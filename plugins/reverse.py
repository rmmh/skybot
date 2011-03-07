'''
Reverses a string

by instanceoftom
'''

from util import hook, http


@hook.command
def reverse(inp):
	".reverse <string> -- reverses the string"
	return inp[::-1]
