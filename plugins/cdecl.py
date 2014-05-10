from util import hook, http


@hook.command
def cdecl(inp):
	'''.cdecl <expr> -- translate between C declarations and English, using cdecl.org'''
	return http.get("http://cdecl.org/query.php", q=inp)
