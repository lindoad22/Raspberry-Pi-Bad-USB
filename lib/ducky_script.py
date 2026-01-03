from adafruit_hid.keycode import Keycode
def get_dict():

    DUCKY_KEYMAP = {

        # Modifiers
        "CTRL": Keycode.CONTROL,
        "SHIFT": Keycode.SHIFT,
        "ALT": Keycode.ALT,
        "WIN": Keycode.WINDOWS,
        "CMD": Keycode.GUI,

        # Basic keys
        "ENTER": Keycode.ENTER,
        "ESC": Keycode.ESCAPE,
        "TAB": Keycode.TAB,
        "SPACE": Keycode.SPACEBAR,
        "BSPACE": Keycode.BACKSPACE,
        "DEL": Keycode.DELETE,
        "CAPS": Keycode.CAPS_LOCK,

        # Arrows
        "UP": Keycode.UP_ARROW,
        "DOWN": Keycode.DOWN_ARROW,
        "LEFT": Keycode.LEFT_ARROW,
        "RIGHT": Keycode.RIGHT_ARROW,

        # Function keys
        "F1": Keycode.F1,
        "F2": Keycode.F2,
        "F3": Keycode.F3,
        "F4": Keycode.F4,
        "F5": Keycode.F5,
        "F6": Keycode.F6,
        "F7": Keycode.F7,
        "F8": Keycode.F8,
        "F9": Keycode.F9,
        "F10": Keycode.F10,
        "F11": Keycode.F11,
        "F12": Keycode.F12,

        # Letters
        "A": Keycode.A,
        "B": Keycode.B,
        "C": Keycode.C,
        "D": Keycode.D,
        "E": Keycode.E,
        "F": Keycode.F,
        "G": Keycode.G,
        "H": Keycode.H,
        "I": Keycode.I,
        "J": Keycode.J,
        "K": Keycode.K,
        "L": Keycode.L,
        "M": Keycode.M,
        "N": Keycode.N,
        "O": Keycode.O,
        "P": Keycode.P,
        "Q": Keycode.Q,
        "R": Keycode.R,
        "S": Keycode.S,
        "T": Keycode.T,
        "U": Keycode.U,
        "V": Keycode.V,
        "W": Keycode.W,
        "X": Keycode.X,
        "Y": Keycode.Y,
        "Z": Keycode.Z,

        # Numbers
        "0": Keycode.ZERO,
        "1": Keycode.ONE,
        "2": Keycode.TWO,
        "3": Keycode.THREE,
        "4": Keycode.FOUR,
        "5": Keycode.FIVE,
        "6": Keycode.SIX,
        "7": Keycode.SEVEN,
        "8": Keycode.EIGHT,
        "9": Keycode.NINE,

}

    return DUCKY_KEYMAP

