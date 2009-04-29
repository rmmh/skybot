# for crusty old rotor

import hook


@hook.command
def profile(inp):
    return 'http://forums.somethingawful.com/member.php?action=getinfo' + \
            '&username=' + '+'.join(inp.split())
