from adafruit_hid.keycode import Keycode
def get_dict():

    DUCKY_KEYMAP = {
    # Modificators
    "CTRL": "CONTROL",
    "CONTROL": "CONTROL",
    "SHIFT": "SHIFT",
    "ALT": "ALT",
    "GUI": "GUI",
    "WIN": Keycode.WINDOWS,
    "CMD": "GUI",

    # Enter / Esc
    "ENTER": Keycode.ENTER,
    "ESC": "ESCAPE",

    # Navigation
    "TAB": "TAB",
    "SPACE": "SPACEBAR",
    "BSPACE": "BACKSPACE",
    "DEL": "DELETE",

    # Arrows
    "UP": "UP_ARROW",
    "DOWN": "DOWN_ARROW",
    "LEFT": "LEFT_ARROW",
    "RIGHT": "RIGHT_ARROW",

    # Function keys
    "F1": "F1",
    "F2": "F2",
    "F3": "F3",
    "F4": "F4",
    "F5": "F5",
    "F6": "F6",
    "F7": "F7",
    "F8": "F8",
    "F9": "F9",
    "F10": "F10",
    "F11": "F11",
    "F12": "F12",

    # Special Keys
    "CAPSLOCK": "CAPS_LOCK",
    "PRINTSCREEN": "PRINT_SCREEN",
    "SCROLLLOCK": "SCROLL_LOCK",
    "PAUSE": "PAUSE",

    # Media
    "VOLUMEUP": "VOLUME_INCREMENT",
    "VOLUMEDOWN": "VOLUME_DECREMENT",
    "MUTE": "MUTE",

    # Znaky (pro STRING parsing)
    "A": "A",
    "B": "B",
    "C": "C",
    "D": "D",
    "E": "E",
    "F": "F",
    "G": "G",
    "H": "H",
    "I": "I",
    "J": "J",
    "K": "K",
    "L": "L",
    "M": "M",
    "N": "N",
    "O": "O",
    "P": "P",
    "Q": "Q",
    "R": Keycode.R,
    "S": "S",
    "T": "T",
    "U": "U",
    "V": "V",
    "W": "W",
    "X": "X",
    "Y": "Y",
    "Z": "Z",

    # Čísla
    "0": "ZERO",
    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",
}

    return DUCKY_KEYMAP

