import inspect
import json
import os


def load():
    return


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
          }
        }''') + '\n')

bot.config = json.load(open('config'))
bot._config_mtime = os.stat('config').st_mtime


def config():
    # reload config from file if file has changed
    if bot._config_mtime != os.stat('config').st_mtime:
        bot.config = json.load(open('config'))
