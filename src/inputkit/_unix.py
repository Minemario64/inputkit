import sys, termios, tty, select
from typing import Callable
from enum import Enum

class Key(Enum):
    UP = b"\x1b[A"
    DOWN = b"\x1b[B"
    LEFT = b"\x1b[D"
    RIGHT = b"\x1b[C"
    INSERT = b"\x1b[2~"
    DEL = b"\x1b[3~"
    HOME = b"\x1b[H"
    END = b"\x1b[F"
    PG_UP = b"\x1b[5~"
    PG_DOWN = b"\x1b[6~"
    ESC = b'\x1b'
    BACKSPACE = b"\x7f"
    ENTER = b"\r"
    TAB = b'\t'
    CTRL_A = b"\x01"
    CTRL_B = b"\x02"
    CTRL_C = b"\x03"
    CTRL_D = b"\x04"
    CTRL_E = b'\x05'
    CTRL_F = b'\x06'
    CTRL_G = b'\x07'
    CTRL_J = b"\n"
    CTRL_K = b"\x0b"
    CTRL_L = b"\x0c"
    CTRL_N = b"\x0e"
    CTRL_O = b'\x0f'
    CTRL_P = b'\x10'
    CTRL_Q = b'\x11'
    CTRL_R = b"\x12"
    CTRL_S = b'\x13'
    CTRL_T = b'\x14'
    CTRL_U = b'\x15'
    CTRL_V = b'\x16'
    CTRL_W = b'\x17'
    CTRL_X = b'\x18'
    CTRL_Y = b'\x19'
    CTRL_Z = b'\x1a'

_FD = sys.__stdin__.fileno() # type: ignore
_OLD_ATTRIBUTES = None

def supportsRawInput():
    if not sys.__stdin__.isatty(): # type: ignore
        return False

    try:
        import termios
        termios.tcgetattr(sys.__stdin__.fileno()) # type: ignore
    except Exception:
        return False

    return True

def disableEcho():
    global _OLD_ATTRIBUTES
    if _OLD_ATTRIBUTES is None:
        _OLD_ATTRIBUTES = termios.tcgetattr(_FD)

    new_attrs = termios.tcgetattr(_FD)
    new_attrs[3] &= ~termios.ECHO  # lflags
    termios.tcsetattr(_FD, termios.TCSADRAIN, new_attrs)

def enableEcho():
    global _OLD_ATTRIBUTES
    if _OLD_ATTRIBUTES is not None:
        termios.tcsetattr(_FD, termios.TCSADRAIN, _OLD_ATTRIBUTES)

import sys
import select

ESC = 0x1B
ESC_TIMEOUT = 0.03

_buffer = bytearray()


def _read_into_buffer(timeout=None):
    r, _, _ = select.select([sys.__stdin__], [], [], timeout)
    if r:
        data = sys.__stdin__.buffer.read1(32) # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        if data:
            _buffer.extend(data)


def _parse_buffer():
    if not _buffer:
        return None

    # Normal key
    if _buffer[0] != ESC:
        return bytes([_buffer.pop(0)])

    # ESC alone (maybe)
    if len(_buffer) == 1:
        return None

    # Alt combo
    if _buffer[1] not in (ord('['), ord('O')):
        return bytes([_buffer.pop(0), _buffer.pop(0)])

    # CSI sequence
    for i in range(2, len(_buffer)):
        b = _buffer[i]
        if 0x40 <= b <= 0x7E:
            seq = bytes(_buffer[:i+1])
            del _buffer[:i+1]
            return seq

    return None


def _getKey() -> bytes:
    while True:
        key = _parse_buffer()
        if key is not None:
            return key

        # If buffer only contains ESC, wait briefly
        if _buffer == b'\x1b':
            _read_into_buffer(ESC_TIMEOUT)
            if len(_buffer) == 1:
                _buffer.clear()
                return b'\x1b'
        else:
            _read_into_buffer(None)

def handleInput(func: Callable[[Key | str], bool], hideCursor: bool = True):
    if hideCursor: print("\x1b[?25l", end='', flush=True)
    fd = sys.__stdin__.fileno() # type: ignore
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)        # raw mode (no line buffering)
        disableEcho()

        going: bool = True

        while going:
            keyBytes: bytes = _getKey()
            try:
                key = Key(keyBytes)

            except ValueError:
                key =  str(keyBytes, 'utf8')

            going = func(key)

    finally:
        enableEcho()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if hideCursor: print("\x1b[?25h", end='', flush=True)

if __name__ == "__main__":
    if supportsRawInput():
        def inputHandler(key: Key | str) -> bool:
            match key:
                case Key.CTRL_C: # Ctrl+C
                    return False # Would Stop handling input, then quit

                case _:
                    if isinstance(key, Key):
                        print(key.name, end='\r\n')

                    else:
                        print(f"{repr(key)}", end="\r\n")

            return True

        handleInput(inputHandler)