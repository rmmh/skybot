"dotnetpad.py: by sklnd, because gobiner wouldn't shut up"

import urllib
import httplib
import json

from util import hook

def dotnetpad(lang, code):
    "Posts a provided snipit of code in a provided langugage to dotnetpad.net"

    params = urllib.urlencode({ 'language': lang
                                ,'code': code})

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    try:
        conn = httplib.HTTPConnection("dotnetpad.net:80")
        conn.request("POST", "/Skybot", params, headers)
        response = conn.getresponse()
    except httplib.HTTPException:
        conn.close()
        return 'dotnetpad is broken somehow, and returned an error'

    try:
        result = json.loads(response.read())
    except ValueError:
        conn.close()
        return 'dotnetpad is broken somehow, and returned an error'

    conn.close()

    if len(result['Errors']) > 0:
        return 'First error: %s' % (result['Errors'][0]['ErrorText'])
    elif len(result['Output']) == 0:
        return 'No output'
    else:
        return result['Output'].lstrip()


@hook.command
def fs(bot, input):
    ".fs -- post a F# code snippit to dotnetpad.net and print the results"

    if len(input.msg) < 4:
        return fs.__doc__

    snipit = input.msg[3:]

    return dotnetpad('fsharp', snipit)

@hook.command
def cs(bot, input):
    ".cs -- post a C# code snippit to dotnetpad.net and print the results"

    if len(input.msg) < 4:
        return cs.__doc__

    snipit = input.msg[3:]

    code = ''
    
    fileTemplate = 'using System; ' \
                   'using System.Linq; ' \
                   'using System.Collections.Generic; ' \
                   'using System.Text; ' \
                   '%(class)s' 

    classTemplate = 'public class Default ' \
                    '{ ' \
                    '    %(main)s ' \
                    '}'

    mainTemplate = 'public static void Main(String[] args) ' \
                   '{ ' \
                   '    %(snipit)s ' \
                   '}' 

    # There are probably better ways to do the following, but I'm feeling lazy
    # if no main is found in the snipit, then we use the template with Main in it
    if snipit.find('public static void Main') == -1:
        code = mainTemplate % { 'snipit': snipit}
        code = classTemplate % { 'main': code }
        code = fileTemplate % { 'class' : code }

    # if Main is found, check for class and see if we need to use the classed template
    elif snipit.find('class') == -1:
        code = classTemplate % { 'main': snipit }
        code = fileTemplate % { 'class' : code }

        return 'Error using dotnetpad'
    # if we found class, then use the barebones template
    else:
        code = fileTemplate % { 'class' : snipit }

    return dotnetpad('csharp', code)




