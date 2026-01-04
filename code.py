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
    def open_html(path):
        with open(path) as f:
            return f.read()
    
    #laoding data from files
    network_file = load_json("/data/network.json")
    users = load_json("/data/login.json")

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
        session_ID = request.cookies
        print(session_ID)

        login_username = users["username"]
        session_ID = {"session_ID":"1"}
        if False == bool(session_ID):
            return Redirect(request, "/login")
            pass
        else:
            
            if request.method == "POST":
                posted_value = request.form_data

                #processing form data 
                data = {key: value for key, value in posted_value.items()}

                #write user input data to json file
                #with open("/data/network.json", 'w') as f:
                #    json.dump(data, f)

            elif request.method == "GET":
                #print("NOT POST")
                pass
            
            html_page = open_html("/static/settings.html")

            return Response(request, html_page.format(
                ssid_value=(ssid),
                wifi_password_value=(wifi_password),
                login_username=(login_username),

            ), content_type="text/html")
    
    #page settings on /login directory
    @server.route("/login", methods=[GET, POST])
    def start(request: Request):
        session_ID = request.cookies

        if False == bool(session_ID):
            

            if request.method == "POST":
                posted_value = request.form_data
                data = {key: value for key, value in posted_value.items()}
                print(data)

                

            html_page = open_html("/static/login.html")
            return Response(request, html_page.format(), content_type="text/html")
        
        else:
            print("redirect")

    @server.route("/script_edit", methods=[GET, POST])
    def edit(request: Request):
        #session_ID = request.cookies

        list_output = ""
        script_file = load_json("/data/scripts.json")
        script = ""
        sc_id = ""
            
        list_item = open_html("/static/list_item.html")
        for key,value in script_file.items():

            l_item = list_item.format(script_id=key, script_name=value["name"], content_type="text/html")
            list_output = list_output + l_item

        if request.method == "GET":

            get = request.query_params

            if len(get) != 0:

                sc_id = get["sc_id"]

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

        html_page = open_html("/static/script_edit.html")
        return Response(request, html_page.format(script=script, list_item=list_output), content_type="text/html")
    
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