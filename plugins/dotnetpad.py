"dotnetpad.py: by sklnd, because gobiner wouldn't shut up"

import urllib.request, urllib.parse, urllib.error

from util import hook, http


def dotnetpad(lang, code):
    "Posts a provided snippet of code in a provided language to dotnetpad.net"

    code = code.encode("utf8")
    params = {"language": lang, "code": code}

    try:
        result = http.get_json(
            "https://dotnetpad.net/Skybot", post_data=params, get_method="POST"
        )
    except http.HTTPError:
        return "error: unable to connect to dotnetpad"

    if result["Errors"]:
        return "First error: %s" % (result["Errors"][0]["ErrorText"])
    elif result["Output"]:
        return result["Output"].lstrip()
    else:
        return "No output"


@hook.command
def fs(inp):
    ".fs -- post a F# code snippet to dotnetpad.net and print the results"

    return dotnetpad("fsharp", inp)


@hook.command
def cs(snippet):
    ".cs -- post a C# code snippet to dotnetpad.net and print the results"

    file_template = (
        "using System; "
        "using System.Linq; "
        "using System.Collections.Generic; "
        "using System.Text; "
        "%s"
    )

    class_template = "public class Default " "{" "    %s \n" "}"

    main_template = "public static void Main(String[] args) " "{" "    %s \n" "}"

    # There are probably better ways to do the following, but I'm feeling lazy
    # if no main is found in the snippet, use the template with Main in it
    if "public static void Main" not in snippet:
        code = main_template % snippet
        code = class_template % code
        code = file_template % code

    # if Main is found, check for class and see if we need to use the
    # classed template
    elif "class" not in snippet:
        code = class_template % snippet
        code = file_template % code

        return "Error using dotnetpad"
    # if we found class, then use the barebones template
    else:
        code = file_template % snippet

    return dotnetpad("csharp", code)
