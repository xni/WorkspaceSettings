#!/usr/bin/env python
"""
This is a simple script, to which I create symlink from .git/hooks/pre-commit.

It checks for
  * trailing whitespaces in every file
  * no new line character at the end of file
  * tabulation in python files
  * PEP8 for committed python files (show warnings)
"""

import re
import subprocess
import sys


TRAILING_WHITESPACE = re.compile(r"\s+\n$")


def get_changed_files():
    """
    Returns a list of files, that are affected by current commit
    """
    process = subprocess.Popen(
        ["git", "diff", "--cached", "--name-only"],
        stdout=subprocess.PIPE)

    stdout, _ = process.communicate()
    return stdout.splitlines()


def check_for_spaces(filename):
    """
    Checks filename for trailing spaces and missing new line
    in the end of file
    """
    errors = []
    with open(filename, "r") as checked_file:
        last_line = None
        for linenum, line in enumerate(checked_file):
            if TRAILING_WHITESPACE.search(line):
                errors.append("{0}:{1}:{2}".format(filename, linenum,
                                                   line.replace(" ", "~")))
            last_line = line

        if last_line and not last_line.endswith("\n"):
            errors.append(r"{0}:\No new line in the end of file".format(
                filename))
    return errors


def check_python(filename):
    """
    Runs PEP8 and tabulation check
    """

    sure_python = False
    if filename.endswith(".py"):
        sure_python = True

    errors = []
    with open(filename, "r") as checked_file:
        for linenum, line in enumerate(checked_file):
            if not sure_python and linenum == 0:
                # if file not *.py it may be script with the first line like
                # "#!/usr/bin/env python"
                if "python" in line:
                    sure_python = True
                else:
                    return []

            if line.startswith("\t"):
                errors.append("{0}:{1}:{2}".format(
                    filename, linenum, line.replace("\t", " \\t ")))

    pep_process = subprocess.Popen(["pep8", filename], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    pep_process.wait()
    if pep_process.stdout.read():
        errors.append("{0}:PEP8 check failed".format(filename))

    return errors


def make_check(filename):
    """
    Checks the file with all tests
    """
    errors = check_for_spaces(filename)
    errors += check_python(filename)
    return errors


def main():
    """
    Main
    """
    if len(sys.argv) == 1:
        changed_files = get_changed_files()
    else:
        changed_files = sys.argv[1:]

    errors = []
    for filename in changed_files:
        errors += make_check(filename)

    if errors:
        print "".join(errors)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
