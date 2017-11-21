# for crusty old rotor

from util import hook


@hook.command
def profile(inp):
    ".profile <username> -- links to <username>'s profile on SA"

    return 'https://forums.somethingawful.com/member.php?action=getinfo' + \
        '&username=' + '+'.join(inp.split())
