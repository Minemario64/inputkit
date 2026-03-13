import os

if os.name == "nt":
    from _win import Key, handleInput

elif os.name == "posix":
    from _unix import Key, handleInput

else:
    raise ImportError("Can't initialize. Only supports windows and posix systems")


__all__ = ["Key", 'handleInput']

# For later, in main / init
"""
import os, subprocess

def spawn_windows_terminal():
    script = os.path.abspath(sys.argv[0])
    args = " ".join(f'"{a}"' for a in sys.argv[1:])
    cmd = f'cmd.exe /k python "{script}" {args}'
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE) # pyright: ignore[reportAttributeAccessIssue]

import shutil

def spawn_linux_terminal():
    script = os.path.abspath(sys.argv[0])
    python = sys.executable
    cmd = f'{python} "{script}" ' + " ".join(f'"{a}"' for a in sys.argv[1:])

    terminals = [
        ["gnome-terminal", "--", "bash", "-c", cmd],
        ["x-terminal-emulator", "-e", cmd],
        ["konsole", "-e", cmd],
        ["xterm", "-e", cmd],
    ]

    for term in terminals:
        if shutil.which(term[0]):
            subprocess.Popen(term)
            return

    raise RuntimeError("No supported terminal emulator found.")
"""