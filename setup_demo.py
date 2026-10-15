"""Creates the 3 demo commits (add, move, fix) in the current git repo.
Run from the repo root:  python setup_demo.py
"""
import subprocess

def git(*args):
    subprocess.run(["git", *args], check=True)

HELPERS = '''def greet(name):
    return "Hello " + name

def check_password(pw):
    if len(pw) > 30:
        return False
    if pw.lower() == "password":
        return False
    if not any(c.isdigit() for c in pw):
        return False
    return True

def bye(name):
    return "Bye " + name
'''

open("helpers.py", "w", newline="\n").write(HELPERS)
git("add", "helpers.py")
git("commit", "-m", "Add helpers")

i, j = HELPERS.index("def check_password"), HELPERS.index("def bye")
open("auth.py", "w", newline="\n").write(HELPERS[i:j].rstrip() + "\n")
open("helpers.py", "w", newline="\n").write(HELPERS[:i] + HELPERS[j:])
git("add", "auth.py", "helpers.py")
git("commit", "-m", "Move check_password to auth.py")

s = open("auth.py").read().replace("> 30", "< 8")
open("auth.py", "w", newline="\n").write(s)
git("add", "auth.py")
git("commit", "-m", "Fix password length check - fixes #3")
print("Done. Now run: python szz_tracer.py . HEAD")