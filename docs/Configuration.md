# Configuration #


Skybot uses a JSON configuration file to hold settings: `/config`

On first run this file is created with default settings:

```json
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
}
```


## Options ##

Connections is an associative array of connection_name : connection_settings
key/value pairs.

`connection_settings:`

Required:

* nick: the name of the bot.
* server: the hostname of the irc server.
* channels: channels to join. A list of strings. Can be []

Optional:

* port: defaults to 6667. The port to connect to.
* user: defaults to "skybot". (user@netmask)
* realname: defaults to "Python bot - http://github.com/rmmh/skybot"
  (Shown in whois)
* server_password: the server password. Omit if not needed.
* nickserv_password: defaults to "" (no login is performed)
* nickserv_name: defaults to "nickserv" (standard on most networks)
* nickserv_command: defaults to "IDENTIFY %s" (interpolated with password)
* ssl: defaults to false. Set to true to connect to the server using SSL
* ignore_cert: defaults to true. Set to false to validate the certificate
  that the remote host uses for the SSL connection.


## Examples ##

A single skybot instance can have multiple connections and multiple channels:

```json
{
  "connections":
  {
    "public bot":
    {
      "server": "irc.example.org",
      "nick": "publicbot",
      "channels": ["#main"]
    },
    "private bot":
    {
      "server": "irc.example.org",
      "nick": "privatebot",
      "channels": ["#secret", "#admin"]
    }
  }
}
```

The user and realname can be set.

* user: defaults to "skybot"
* realname: defaults to "Python bot - http://github.com/rmmh/skybot"

```json
{
  "connections":
  {
    "poker irc":
    {
      "server": "irc.poker.example.com",
      "nick": "pokerbot",
      "channels": ["#poker"],
      "user": "pokerbot",
      "realname": "Pokerbot - a fork of Skybot",
    }
  }
}
```

Automatic identification is possible.

* nickserv_password: defaults to "" (no login is performed)
* nickserv_name: defaults to "nickserv" (standard on most networks)
* nickserv_command: defaults to "IDENTIFY %s" (interpolated with password)

```json
{
  "connections":
  {
    "poker irc":
    {
      "server": "irc.poker.example.com",
      "nick": "pokerbot",
      "nickserv_password": "aceofspades",
      "channels": ["#poker"]
    }
  }
}
```
