import time
import usb_hid
import wifi
import socketpool
import json
import ducky_script
from fce import load_json

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

from adafruit_httpserver import GET,POST, Request, Response, Server

def attack_mode():
    #load ducky_script keymap
    dictionary = ducky_script.get_dict()
    #print(dictionary)
    
    #
    active_id = load_json("/data/active_script.json")["active_script_id"]
    active_script = load_json("/data/scripts.json")[active_id]

    split_script = active_script["script"].split(",")

    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)

    for i in split_script:
        if "+" in i:
            i_split = i.split("+")
            #print(i_split)
            
            for x in i_split:
                key = dictionary[x]
                #print(key)
                
                #kbd.press(key)
                print("pressing")


            time.sleep(0.2)
            kbd.release_all()
            print("keys released")

        elif "[" and "]" in i:
            #layout.write(i[1:-1])
            print("writing")

        else:
            key = dictionary[i]
            #kbd.send(key)
            


            

    

def config_mode():
    def open_html(path):
        with open(path) as f:
            return f.read()
    
    with open("/data/network.json") as f:
        network_file = json.load(f)

    print(network_file)
    
    ssid = network_file["ssid"]
    wifi_password = network_file["wifi_password"]
    script = ""


    print("creating AP")
    #time.sleep(3)
    wifi.radio.start_ap(ssid=ssid, password=wifi_password)

    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)
    

    #file = [('ssid', 'test'), ('ip_address', '192'), ('wifi_password', '12345678'), ('script', 'Script')]
    #print(file[0])

    
    @server.route("/", methods=[GET, POST])
    def index(request: Request):

        if request.method == "POST":
            posted_value = request.form_data

            data = {key: value for key, value in posted_value.items()}
            print(data)

            with open("/data/network.json", 'w') as f:
                json.dump(data, f)
        elif request.method == "GET":
            print("NOT POST")
        
        html_page = open_html("/static/settings.html")

        return Response(request, html_page.format(
            ssid_value=(ssid),
            wifi_password_value=(wifi_password),
            script=(script)

        ), content_type="text/html")
    
    
    

    server.serve_forever(str(wifi.radio.ipv4_address_ap))
    
attack_mode()
#config_mode()

while True:
    time.sleep(1)