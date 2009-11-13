from util import hook
from pycparser.cdecl import explain_c_declaration

@hook.command('explain')
def explain(inp):
    '''.explain char *(*(**foo[][8])())[]; -- returns :
foo is a array of array[8] of pointer to pointer to function() returning pointer
 to array of pointer to char
'''
    if not inp:
        return ""

    try:    
        result = explain_c_declaration(inp.rstrip())
    except e:
        result = str(e)

    return result

