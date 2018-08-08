from util import hook, http


@hook.command
def cdecl(inp):
	'''.cdecl <expr> -- translate between C declarations and English, using cdecl.org'''
	return http.get("https://xwd733f66f.execute-api.us-west-1.amazonaws.com/prod/cdecl_backend", q=inp)
