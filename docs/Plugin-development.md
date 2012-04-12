# Plugin development #


> This documentation page needs to be improved. Contributions are welcomed.

##Overview ##

Skybot continually scans the `plugins/` directory for new or changed .py
files. When it finds one, it runs it and examines each function to see whether
it is a plugin hook.

All plugins need to `from util import hook` in order to be callable.


## A simple example ##

plugins/echo.py:

```python
from util import hook

@hook.command
def echo(inp):
    return inp + inp
```

usage:

    <rmmh> .echo hots
    <skybot> Scaevolus: hotshots


This plugin example defines a command that replies with twice its input. It
can be invoked by saying phrases in a channel the bot is in, notably ".echo",
"skybot: echo", and "skybot, echo" (assuming the bot's nick is "skybot").


## Plugin hooks ##

There are four types of plugin hooks: commands, regexes, events, and sieves.
The hook type is assigned to plugin functions using decorators found
in `util/hook.py`.


There is also a secondary hook decorator: `@hook.singlethread`

It indicates that the function should run in its own thread. Note that, in
that case, you can't use the existing database connection object.

### Shared arguments ###

> This section has to be verified.

These arguments are shared by functions of all hook types:

* nick -- string, the nickname of whoever sent the message.
* channel -- string, the channel the message was sent on. Equal to nick if
  it's a private message.
* msg -- string, the line that was sent.
* raw -- string, the raw full line that was sent.
* re -- the result of doing `re.match(hook, msg)`.
* bot -- the running bot object.
* db -- the database connection object.
* input -- the triggering line of text

### Commands hook ###

`@hook.command`
`@hook.command(command_name)`

Commands run when the beginning of a normal chat line matches one of
`.command`, `botnick: command`, or `botnick, command`, where `command` is the
command name, and `botnick` is the bot's nick on the server.

Commands respond to abbreviated forms: a command named "`dictionary`" will be
invoked on both "`.dictionary`" and "`.dict`". If an abbreviated command is
ambiguous, the bot will return with a list of possibilities: given commands
"`dictionary`" and "`dice`", attempting to run command "`.di`" will make the
bot say "`did you mean dictionary or dice?`".

When `@hook.command` is used without arguments, the command name is set to the
function name. When given an argument, it is used as the command name. This
allows one function to respond to multiple commands:

```python
from util import hook

@hook.command('hi')
@hook.command
def hello(inp):
    return "Hey there!"
```

Users can invoke this function with either "`.hello`" or "`.hi`".

### Regexes hook ###

> This section needs to be improved.

`@hook.regex(pattern)`

Each line of chat is matched against the provided regex pattern. If it is
successful, the hook function will be called with the matched object.

```python
from util import hook

@hook.regex("lame bot")
def hurtfulcomment(match):
    return "I have FEELINGS!"
```

### Events hook ###

> This section needs to be improved.

`@hook.event(irc_command)`

Event hooks are called whenever a specific IRC command is issued. For example,
if you provide "*" as parameter, it will trigger on every line. If you provide
"PRIVMSG", it will only trigger on actual lines of chat (not nick-changes).

The first argument in these cases will be a two-element list of the form
["#channel", "text"].

### Sieves hook ###

> This section needs to be improved.

`@hook.sieve`

Sieves can prevent commands, regexes, and events from running.

For instance, commands could be tagged as admin-only, and then a sieve would
verify that the user invoking the command has the necessary privileges.

The function must take 5 arguments: (bot, input, func, type, args).
To cancel a call, return None.

## Available objects ##

> This section needs to be written.

### The bot object ###

### The db object ###

### The input object ###
