import time

from util import hook, http

prompt = [0,
    {"role": "system", "content":
     "You are a terse and helpful assistant named SkyboGPT, answering questions briefly with one or two sentences. Answer as concisely as possible."},
]


@hook.api_key("openai")
@hook.command("gpt")
@hook.command
def chatgpt(inp, api_key=None, reply=None):
    ".gpt/.chatgpt <query> -- asks ChatGPT a question"

    global prompt

    if not api_key:
        return

    if inp == 'clear':
        prompt = prompt[:2]
        return

    if prompt[0] < time.time() - 60 * 10:  # forget after 10 minutes
        prompt = prompt[:2]

    prompt.append({"role": "user", "content": inp})

    url = "https://api.openai.com/v1/chat/completions"
    result = http.get_json(url, headers={'Authorization': 'Bearer ' + api_key}, json_data={
        "model": "gpt-3.5-turbo",
        "messages": prompt[1:]
    })

    if 'error' in result:
        reply(result['error']['message'])

    msg = result['choices'][0]['message']
    prompt[0] = time.time()
    prompt.append(msg)

    for line in prompt[1:]:
        print(line['role'] + ':', line['content'])
    print(result['usage'])

    if result['usage']['total_tokens'] > 2048:
        prompt.pop(2)

    reply(msg['content'].replace('\n', '  '))
