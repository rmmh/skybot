from os import path
import json
import inspect


def get_fixture_file(testcase, file):
    filename = inspect.getfile(testcase.__class__)

    test_name, _ = path.splitext(filename)
    dir_path = path.dirname(path.realpath(filename))

    with open(path.join(dir_path, test_name, file)) as f:
        return f.read()


def get_fixture_file_data(testcase, file):
    return json.loads(get_fixture_file(testcase, file))


def execute_skybot_regex(command_method, inp, **kwargs):
    for type, (func, func_args) in command_method._hook:
        if not type == 'regex' or 're' not in func_args:
            continue

        search_result = func_args['re'].search(inp)

        if search_result:
            return command_method(search_result, **kwargs)

    return None
