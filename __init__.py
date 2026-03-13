import os

if os.name == "nt":
    from _win import Key, handleInput

elif os.name == "posix":
    from _unix import Key, handleInput

else:
    raise ImportError("Can't initialize. Only supports windows and posix systems")


__all__ = ["Key", 'handleInput']