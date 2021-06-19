from builtins import map
import re

from util import hook


@hook.sieve
def sieve_suite(bot, input, func, kind, args):
    if (
        input.command == "PRIVMSG"
        and bot.config.get("ignorebots", True)
        and input.nick.lower()[-3:] == "bot"
        and args.get("ignorebots", True)
    ):
        return None

    if kind == "command":
        if input.trigger in bot.config.get("disabled_commands", []):
            return None

        ignored = bot.config.get("ignored", [])
        if input.host in ignored or input.nick in ignored:
            return None

    fn = re.match(r"^plugins.(.+).py$", func._filename)
    disabled = bot.config.get("disabled_plugins", [])
    if fn and fn.group(1).lower() in disabled:
        return None

    acls = bot.config.get("acls", {})
    for acl in [acls.get(func.__name__), acls.get(input.chan), acls.get(input.server)]:
        if acl is None:
            continue
        if "deny-except" in acl:
            allowed_channels = [x.lower() for x in acl["deny-except"]]
            if input.chan.lower() not in allowed_channels:
                return None
        if "allow-except" in acl:
            denied_channels = [x.lower() for x in acl["allow-except"]]
            if input.chan.lower() in denied_channels:
                return None
        if "whitelist" in acl:
            if func.__name__ not in acl["whitelist"]:
                return None
        if "blacklist" in acl:
            if func.__name__ in acl["whitelist"]:
                return None
        if "blacklist-nicks" in acl:
            if input.nick.lower() in acl["blacklist-nicks"]:
                return None

    admins = input.conn.admins
    input.admin = input.host in admins or input.nick in admins

    if args.get("adminonly", False):
        if not input.admin:
            return None

    return input
