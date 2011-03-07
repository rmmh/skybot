'''

Reverses a string
 	
by instanceoftom
'''

from util import hook


@hook.command
11	 	
def reverse(inp):
12	 	
  ".reverse <string> -- reverses the string"
13	 	
  return inp[::-1]
 
