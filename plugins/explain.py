from pycparser.cdecl import explain_c_declaration

@hook.command('explain')
def explain(inp):
    '''.explain char *(*(**foo[][8])())[]; -- returns :
foo is a array of array[8] of pointer to pointer to function() returning pointer
 to array of pointer to char
'''
    if not inp:
        return None
    
    result = explain_c_declaration(inp)
    if result: return result
    else: return None