from util import hook
from pycparser.cdecl import explain_c_declaration

@hook.command('explain')
def explain(inp):
    ".explain <c expression> -- gives an explanation of C expression"
    if not inp:
        return explain.__doc__

    inp = inp.encode('utf8', 'ignore')

    try:    
        return explain_c_declaration(inp)
    except Exception, e:
        return 'error: %s' % e
