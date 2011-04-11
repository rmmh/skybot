
from util import http,hook
import re

video_regex = (r'(?i)http://(?:www\.)?vimeo.com/([A-Za-z0-9\-]+)')
r'([a-zA-Z]+://|www\.)[^ ]+'
video_request_base = "http://vimeo.com/api/v2/video/%s.json"

video_info = "\x02%(title)s\x02 - length \x02%(duration)ss\x02 - \x02%(stats_number_of_likes)s\x02 likes - \x02%(stats_number_of_plays)s\x02 plays - \x02%(user_name)s\x02 on \x02%(upload_date)s\x02"


def viemo_video_info(video_id):

	json_url = video_request_base % (video_id,)

	json_responses = http.get_json(json_url)

	if json_responses:

		video_details = json_responses[0]

		return video_info % video_details


@hook.regex(video_regex)
def viemo_url(url_match):
	return viemo_video_info(url_match.group(1))
