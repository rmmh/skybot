import time

from util import hook, http


commands_modtime = 0
commands = {}


def update_commands(force=False):
    global commands_modtime, commands

    if force or time.time() - commands_modtime > 60 * 60:  # update hourly
        h = http.get_html('http://wiki.github.com/nslater/oblique/')

        lines = h.xpath('//li/text()')
        commands = {}
        for line in lines:
            if not line.strip():
                continue

            name, url = line.strip().split(None, 1)
            commands[name] = url

        commands_modtime = time.time()


@hook.command('o')
@hook.command
def oblique(inp, nick='', chan=''):
    '.o/.oblique <command> <args> -- runs <command> using oblique web'
    ' services. see http://wiki.github.com/nslater/oblique/'

    update_commands()

    if ' ' in inp:
        command, args = inp.split(None, 1)
    else:
        command = inp
        args = ''

    command = command.lower()

    if command == 'refresh':
        update_commands(True)
        return '%d commands loaded.' % len(commands)
    if command in commands:
        url = commands[command]
        url = url.replace('${nick}', nick)
        url = url.replace('${sender}', chan)
        url = url.replace('${args}', http.quote(args.encode('utf8')))
        try:
            return http.get(url)
        except http.HTTPError, e:
            return "http error %d" % e.code
    else:
        return 'no such service'
