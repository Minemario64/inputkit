import msvcrt
from enum import Enum
from typing import Callable, overload

class Key(Enum):
    UP = "H"
    DOWN = "P"
    LEFT = "K"
    RIGHT = "M"
    INSERT = "R"
    DEL = "S"
    HOME = "G"
    END = "O"
    PG_UP = "I"
    PG_DOWN = "Q"
    ESC = '\x1b'
    BACKSPACE = "\x08"
    ENTER = "\r"
    TAB = '\t'
    CTRL_A = "\x01"
    CTRL_B = "\x02"
    CTRL_C = "\x03"
    CTRL_D = "\x04"
    CTRL_E = '\x05'
    CTRL_F = '\x06'
    CTRL_G = '\x07'
    CTRL_J = "\n"
    CTRL_K = "\x0b"
    CTRL_L = "\x0c"
    CTRL_N = "\x0e"
    CTRL_O = '\x0f'
    CTRL_P = '\x10'
    CTRL_Q = '\x11'
    CTRL_R = "\x12"
    CTRL_S = '\x13'
    CTRL_T = '\x14'
    CTRL_U = '\x15'
    CTRL_V = '\x16'
    CTRL_W = '\x17'
    CTRL_X = '\x18'
    CTRL_Y = '\x19'
    CTRL_Z = '\x1a'

def _getkey() -> str | Key:
    ch: str = msvcrt.getwch()
    if ch in ('à', '\x00'):
        ID = msvcrt.getwch()
        try:
            return Key(ID)

        except ValueError:
            return f"{ch}{ID}"

    if ch.isalpha():
        return ch

    try:
        return Key(ch)

    except ValueError:
        return ch

@overload
def handleInput(callback: Callable[[Key | str], bool]) -> None: ...

@overload
def handleInput(callback: None = None, *, hideCursor: bool = True) -> Callable: ...

def handleInput(callback: Callable[[str | Key], bool] | None = None,*, hideCursor: bool = True):
    def wrapper(callback: Callable[[str | Key], bool]):
        going: bool = True
        if hideCursor: print("\x1b[?25l", end='', flush=True)
        while going:
            going = callback(_getkey())

        if hideCursor: print("\x1b[?25h", end='', flush=True)

    if callback is None:
        return wrapper

    wrapper(callback)

if __name__ == "__main__":
    @handleInput
    def inputHandler(key: Key | str) -> bool:
        match key:
            case Key.CTRL_C: # Ctrl+C
                return False # Would Stop handling input, then quit

            case _:
                if isinstance(key, Key):
                    print(key.name)

                else:
                    print(f"{repr(key)}")

        return True