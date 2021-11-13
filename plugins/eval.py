import time
import uuid
import json

from util import hook, http


def piston(language, version, content, filename=None):
    api_url = "https://emkc.org/api/v2/piston/execute"

    if not filename:
        filename = str(uuid.uuid1())

    payload = {
        "language": language,
        "version": version,
        "files": [{"name": filename, "content": content}],
        "stdin": "",
        "args": [],
        "compile_timeout": 5000,
        "run_timeout": 5000,
        "compile_memory_limit": -1,
        "run_memory_limit": -1,
    }

    headers = {"Content-Type", "application/json"}

    result = http.get_json(api_url, json_data=payload, get_methods="POST")

    if result["run"]["stderr"] != "":
        return "Error: " + result["run"]["stderr"]

    return result["run"]["output"].replace("\n", " ")

@hook.command
def cpp(inp, nick=None):
    headers = ['algorithm', 'any', 'array', 'atomic', 'bit', 'bitset',
               'cassert', 'ccomplex', 'cctype', 'cerrno', 'cfenv', 'cfloat',
               'charconv', 'chrono', 'cinttypes', 'ciso646', 'climits',
               'clocale', 'cmath', 'codecvt', 'complex', 'complex.h',
               'condition_variable', 'csetjmp', 'csignal', 'cstdalign',
               'cstdarg', 'cstdbool', 'cstddef', 'cstdint', 'cstdio',
               'cstdlib', 'cstring', 'ctgmath', 'ctime', 'cuchar', 'cwchar',
               'cwctype', 'cxxabi.h', 'deque', 'exception', 'execution',
               'fenv.h', 'filesystem', 'forward_list', 'fstream',
               'functional', 'future', 'initializer_list', 'iomanip', 'ios',
               'iosfwd', 'iostream', 'istream', 'iterator', 'limits', 'list',
               'locale', 'map', 'math.h', 'memory', 'memory_resource', 'mutex',
               'new', 'numeric', 'optional', 'ostream', 'queue', 'random',
               'ratio', 'regex', 'scoped_allocator', 'set', 'shared_mutex',
               'sstream', 'stack', 'stdexcept', 'stdlib.h', 'streambuf',
               'string', 'string_view', 'system_error', 'tgmath.h', 'thread',
               'tuple', 'typeindex', 'typeinfo', 'type_traits',
               'unordered_map', 'unordered_set', 'utility', 'valarray',
               'variant', 'vector', 'version']
    header_includes = "\n".join([f"#include <{x}>" for x in headers])
    contents = f"""
        {header_includes}
        using namespace std;
        using namespace std::chrono_literals;
        using namespace std::complex_literals;
        using namespace std::string_literals;
        using namespace std::string_view_literals;
        int main() {{
            {inp};
        }}
    """
    return piston("c++", "10.2.0", contents, filename=nick)


@hook.command
def lua(inp, nick=None):
    return piston("lua", "5.4.2", inp, filename=nick)


@hook.command("cl")
def lisp(inp, nick=None):
    return piston("lisp", "2.1.2", inp, filename=nick)


@hook.command("elisp")
@hook.command("el")
def emacs(inp, nick=None):
    return piston("emacs", "27.1.0", inp, filename=nick)


@hook.command("clj")
def clojure(inp, nick=None):
    return piston("clojure", "1.10.3", inp, filename=nick)


@hook.command("rs")
def rust(inp, nick=None):
    contents = "func main() {" + inp + "}";
    return piston("rust", "1.50.0", contents, filename=nick)


@hook.command("py")
@hook.command("py3")
def python(inp, nick=None):
    return piston("python", "3.10.0", inp, filename=nick)


@hook.command("py2")
def python2(inp, nick=None):
    return piston("python2", "2.7.18", inp, filename=nick)


@hook.command("rb")
def ruby(inp, nick=None):
    return piston("ruby", "3.0.1", inp, filename=nick)


@hook.command("ts")
def typescript(inp, nick=None):
    return piston("typescript", "4.2.3", inp, filename=nick)


@hook.command("js")
@hook.command("node")
def javascript(inp, nick=None):
    return piston("javascript", "16.3.0", inp, filename=nick)


@hook.command
def perl(inp, nick=None):
    return piston("perl", "5.26.1", inp, filename=nick)


@hook.command
def php(inp, nick=None):
    contents = "<?php" + inp + "?>"
    return piston("php", "8.0.2", contents, filename=nick)


@hook.command
def swift(inp, nick=None):
    return piston("swift", "5.3.3", inp, filename=nick)


if __name__ == "__main__":
    result = piston("py", "3.9.4", "print('test')")

    print(result)
