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

from adafruit_httpserver import GET,POST, Request, Response, Server, Headers, Redirect, NOT_FOUND_404, MOVED_PERMANENTLY_301

#sd card imports
import adafruit_sdcard
import busio
import digitalio
import board
import storage  


# button = digitalio.DigitalInOut(board.GP15)
# button.switch_to_input(pull=digitalio.Pull.UP)
# while True:
#     if button.value == False:
#         print("pushed")
#     else:
#         print("not pushed")

#     time.sleep(0.2)


sck = board.GP18
mosi = board.GP19   
miso = board.GP16
cs = digitalio.DigitalInOut(board.GP17)

spi = busio.SPI(sck, mosi, miso)

#mounting SD card
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

def attack_mode():
    #load ducky_script keymap
    dictionary = ducky_script.get_dict()
    #print(dictionary)
    
    #loading json file with active script ID
    active_id = load_json("/data/active_script.json")["active_script_id"]
    #loading active attack script from json file
    active_script = load_json("/data/scripts.json")[active_id]
    split_script = active_script["script"].split(",")

    #set keyboard
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)


    #Generating HID inputs from ducky script
    for i in split_script:
        if "+" in i:
            i_split = i.split("+")
            #print(i_split)
            
            for x in i_split:
                key = dictionary[x]
                #print(key)
                
                kbd.press(key)
                print("pressing")


            time.sleep(0.2)
            kbd.release_all()
            print("keys released")

        elif "[" and "]" in i:
            layout.write(i[1:-1])
            print("writing")

        elif "WAIT" in i:
            t = i[4:]
            time.sleep(float(t))

        else:
            key = dictionary[i]
            kbd.send(key)

    
    #log attack to file

def config_mode():

    headers = Headers()
    def open_html(path):
        with open(path) as f:
            return f.read()
    
    #laoding data from files
    network_file = load_json("/sd/network.json")
    users = load_json("/sd/login.json")

    ssid = network_file["ssid"]
    wifi_password = network_file["wifi_password"]

    print("creating AP")
    #time.sleep(3)
    wifi.radio.start_ap(ssid=ssid, password=wifi_password)

    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)

    #page settings on root directory
    @server.route("/", methods=[GET, POST])
    def index(request: Request):

        #request cookies
        session_ID = request.headers.get("Cookie", "")
        #print(session_ID)

        login_username = users["username"]
        #session_ID = {"session_ID":"1"}

        message = ""
        if False == bool(session_ID):
            return Redirect(request, "/login")
            pass
        else:
            
            if request.method == "POST":
                posted_value = request.form_data

                #processing form data 
                data = {key: value for key, value in posted_value.items()}

                #write user input data to json file
                with open("/sd/network.json", 'w') as f:
                    json.dump(data, f)
                message="Settings saved"

            elif request.method == "GET":
                #print("NOT POST")
                pass
            
            html_page = open_html("/static/settings.html")

            return Response(request, html_page.format(
                ssid_value=(ssid),
                wifi_password_value=(wifi_password),
                login_username=(login_username),
                message=(message)

            ), content_type="text/html")
    
    #page settings on /login directory
    @server.route("/login", methods=[GET, POST])
    def start(request: Request):
        session_ID = request.headers.get("Cookie", "")

        print(session_ID)
        if False == bool(session_ID):
            
            message = ""
            if request.method == "POST":
                posted_value = request.form_data
                data = {key: value for key, value in posted_value.items()}

                login_file = load_json("/data/login.json")
                if data["username"] == login_file["username"]:
                    if data['password'] == login_file['password']:
                        #cookies = {"session_ID": "1"}

                        headers = Headers()
                        headers.add("Set-Cookie", "session_ID=1; Path=/")
                        print("headers set")
                        return Redirect(request, "/",headers=headers)
                    else:
                        message = "wrong username or password"
                        print(message)

                else:
                        message = "wrong username or password"
                        print(message)

                
            
            html_page = open_html("/static/login.html")
            return Response(request, html_page.format(message=message), content_type="text/html")
        
        else:
            return Redirect(request, "/")

    @server.route("/script_edit", methods=[GET, POST])
    def edit(request: Request):
        #session_ID = request.cookies

        list_output = ""
        script_file = load_json("/data/scripts.json")
        active_script = load_json("/data/active_script.json")
        active_script_id = active_script['active_script_id']
        script = ""
        sc_id = ""
        message =""

        list_item = open_html("/static/list_item.html")
        for key,value in script_file.items():

            l_item = list_item.format(script_id=key, script_name=value["name"], content_type="text/html")
            list_output = list_output + l_item

        checked = ""
        if request.method == "GET":

            get = request.query_params

            if len(get) != 0:

                sc_id = get["sc_id"]
                print(sc_id)
                print(active_script_id)

                try:

                    script = script_file[sc_id]["script"]
                except:
                    pass

        if request.method == "POST":
            posted_value = request.form_data
            get = request.query_params
            
            if len(get) != 0:

                data = {key: value for key, value in posted_value.items()}
                print(data)
                #print(get["sc_id"])

                script_file[get['sc_id']]["script"] = data["script"]
                print(script_file)
                message = "Script saved"

        html_page = open_html("/static/script_edit.html")
        return Response(request, html_page.format(checked=checked,script=script, list_item=list_output, message=message), content_type="text/html")
    
    @server.route("/logbook", methods=[GET, POST])
    def edit(request: Request):

        html_page = open_html("/static/logbook.html")
        
        logs = []
        with open("/data/logs.ndjson") as f:
            for line in f:
                logs.append(json.loads(line))

        list_item = open_html("/static/log_item.html")
        list_output = ""
        for i in logs:
            print(i)
            
            l_item = list_item.format(id=i["id"], status=i["status"], reason=i["reason"],script_name=i["script_name"], content_type="text/html")
            list_output = list_output + l_item
        
        
        return Response(request, html_page.format(logbook_item=list_output), content_type="text/html")

    server.serve_forever(str(wifi.radio.ipv4_address_ap))
    
#attack_mode()
config_mode()

while True:
    time.sleep(1)