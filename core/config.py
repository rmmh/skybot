import os

from util import yaml

if not os.path.exists('config'):
    conf = {'connections': [
        {'local irc': 
            {'nick': 'skybot',
             #'user': 'skybot',
             #'realname': 'Python bot - http://bitbucket.org/Scaevolus/skybot/',
             'server': 'localhost',
             #'port': 6667,
             'channels': ["#test"],
             #'nickserv_password', 'password',
             #'nickserv_name': 'nickserv',
             #'nickserv_command': 'IDENTIFY %s'
            }
        }
        ]}
    yaml.dump(conf, open('config', 'w'))
    del conf

bot.config = yaml.load(open('config'))
bot._config_dirty = True # force a rewrite on start
bot._config_mtime = os.stat('config').st_mtime

def config_dirty(self): 
    "signals that config has changed and should be written to disk"
    self._config_dirty = True

bot.config_dirty = config_dirty

def config():
    # reload config from file if file has changed
    if bot._config_mtime != os.stat('config').st_mtime:
        bot.config = yaml.load(open('config'))
        bot._config_dirty = False

    # save config to file if config has changed
    if bot._config_dirty:
        yaml.dump(bot.config, open('config', 'w'))
