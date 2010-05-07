import inspect
import json
import os


def save(conf):
    json.dump(conf, open('config', 'w'), sort_keys=True, indent=2)

if not os.path.exists('config'):
    open('config', 'w').write(inspect.cleandoc(
        '''
        {
          "connections":
          {
            "local irc":
            {
              "server": "localhost",
              "nick": "skybot",
              "channels": ["#test"]
            }
          },
          "disabled_plugins": [],
          "disabled_commands": [],
          "acls": {}
        }''') + '\n')


def config():
    # reload config from file if file has changed
    if bot._config_mtime != os.stat('config').st_mtime:
        try:
            bot.config = json.load(open('config'))
        except ValueError, e:
            print 'ERROR: malformed config!', e


bot._config_mtime = 0
