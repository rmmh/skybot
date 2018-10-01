import re
from functools import wraps
from time import time

from util import hook, http


CDECL_URL = "https://cdecl.org/"
RE_QUERY_ENDPOINT = re.compile('var QUERY_ENDPOINT = "([^"]+)"')
QUERY_URL_MEMO_TTL = 600


def memoize(ttl):
	def _memoizer(f):
		@wraps(f)
		def wrapper(*args, **kwargs):
			if hasattr(wrapper, 'memo') and wrapper.memo:
				memo_time, result = wrapper.memo
				if time() - memo_time < ttl:
					return result

			result = f(*args, **kwargs)
			wrapper.memo = (time(), result)
			return result
		return wrapper
	return _memoizer


@memoize(QUERY_URL_MEMO_TTL)
def get_cdecl_query_url():
	print("RUNNING")
	result = http.get(CDECL_URL)

	match = RE_QUERY_ENDPOINT.search(result)

	if not match:
		return None

	return match.group(1)


@hook.command
def cdecl(inp):
	'''.cdecl <expr> -- translate between C declarations and English, using cdecl.org'''
	query_url = get_cdecl_query_url()

	if not query_url:
		return "cannot find CDECL query url"

	return http.get(query_url, q=inp)
