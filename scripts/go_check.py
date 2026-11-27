#!/usr/bin/env python

""" Check Go source files: each must be formatted as gofmt formats it and
must pass go vet. Invoked by the checker as go_check.py <file.go>...

What go vet is given depends on where the file lives:

- in a directory that holds several programs (more than one file has a
  func main), the file is vetted on its own;
- under a directory with a go.mod, the module is vetted (go vet ./...);
- otherwise with the other files of its directory, as the package they
  form (a library and its tests, a program split over files).

Some slide listings are not meant to build: a fragment shown with .code,
a program whose compile error is the lesson, an example that imports a
package this repository does not hold. Such a file says so on its first
line:

    // vet: expect "undefined: Stack" - the type is on another slide OMIT

Then go vet (or gofmt, when the file does not even parse) must fail, and
its output must contain the quoted text: the file is still checked, for
the one failure it declares. The trailing OMIT hides the line from the
slides. """

import os
import re
import subprocess
import sys

EXPECT = re.compile(r'^// vet: expect "([^"]+)"')
MAIN = re.compile(r"^func main\(", re.MULTILINE)


def run(cmd, cwd=None):
    """ Run a command and return (exit code, combined output). """
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout + proc.stderr


def read(path):
    """ The text of a source file. """
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def module_root(directory):
    """ The nearest directory at or above `directory`, inside the repository,
    that has a go.mod; None when there is none. """
    current = os.path.abspath(directory)
    top = os.getcwd()
    while current.startswith(top):
        if os.path.isfile(os.path.join(current, "go.mod")):
            return current
        if current == top:
            break
        current = os.path.dirname(current)
    return None


def vet(path):
    """ Run go vet on what `path` belongs to. """
    directory = os.path.dirname(path) or "."
    siblings = sorted(
        os.path.join(directory, name) for name in os.listdir(directory) if name.endswith(".go")
    )
    programs = [s for s in siblings if MAIN.search(read(s))]
    if len(programs) > 1:
        return run(["go", "vet", os.path.basename(path)], cwd=directory)
    root = module_root(directory)
    if root is not None:
        return run(["go", "vet", "./..."], cwd=root)
    # the listings that declare a failure of their own are not part of the package
    package = [s for s in siblings if not EXPECT.match(read(s)) or s == path]
    return run(["go", "vet", *package])


def check(path):
    """ The complaints about one file; empty when it is fine. """
    expected = EXPECT.match(read(path))
    code, output = run(["gofmt", "-l", path])
    if expected is not None:
        if code != 0:
            # it does not parse: that must be the failure it declares
            return [] if expected.group(1) in output else [f"{path}: gofmt failed otherwise:\n{output}"]
        if output.strip():
            return [f"{path}: not formatted (run gofmt -w)"]
        code, output = vet(path)
        if code == 0:
            return [f'{path}: go vet passed, but the file expects "{expected.group(1)}"']
        if expected.group(1) not in output:
            return [f"{path}: go vet failed otherwise:\n{output}"]
        return []
    if code != 0:
        return [f"{path}: gofmt failed:\n{output}"]
    if output.strip():
        return [f"{path}: not formatted (run gofmt -w)"]
    code, output = vet(path)
    if code != 0:
        return [f"{path}: go vet failed:\n{output}"]
    return []


def main():
    """ main entry point """
    complaints = []
    for path in sys.argv[1:]:
        complaints.extend(check(path))
    for complaint in complaints:
        print(complaint, file=sys.stderr)
    sys.exit(1 if complaints else 0)


if __name__ == "__main__":
    main()
