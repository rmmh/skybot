from util import http, hook
from urllib2 import HTTPError
import re
from string import Template

# http://www.redmine.org/projects/redmine/wiki/Rest_api

@hook.api_key('redmine')
@hook.command('issue')
def issue(inp, api_key=None):
    ".issue <id> -- link to a Redmine issue <id>"

    # Validate configuration.
    if api_key is None:
        # This won't work without an API key.
        return "ConfigurationError: No API access configured."
    if not isinstance(api_key, dict):
        return "ConfigurationError: API config must be a dictionary."
    if any(key not in api_key for key in ('url', 'key')):
        return "ConfigurationError: Both root url and key required."

    # Parse the input argument.
    match = re.match(r'^\#?(\d+)$', inp)
    try:
        # If an issue number is specified, use it for the URL
        request_url = api_key['url'] + match.group(1) + '.json'
    except (AttributeError, IndexError):
        # Otherwise if it doesn't look like an id, reply with error.
        return "ValueError: invalid id"

    query_params = {'key': api_key['key']}

    # Make the HTTP request and parse the JSON response.
    try:
        data = http.get_json(request_url, query_params=query_params)
    except HTTPError, e:
        return str(e)

    issue = data['issue']
    issue['url'] = api_key['url'] + str(issue['id'])

    t = Template("Issue #$id $subject $url")

    # Render the response.
    return t.substitute(**issue)
