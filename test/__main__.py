from os import path
from unittest import TestSuite, TestLoader, TextTestRunner
import sys

if __name__ == '__main__':
    # Because the project is structured differently than
    # any tooling expects, we need to modify the python
    # path during runtime (or before) to get it to
    # properly import plugins and other code correctly.
    project_root_directory = path.dirname(path.dirname(__file__))

    sys.path.append(path.join(project_root_directory, 'plugins'))
    sys.path.append(path.join(project_root_directory))

    discovered_tests = TestLoader().discover(path.dirname(__file__))
    run_result = TextTestRunner().run(discovered_tests)

    if not run_result.wasSuccessful():
        sys.exit(1)
