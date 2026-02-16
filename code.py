import time
import usb_hid
import wifi
import socketpool
import ducky_script
from fce import load_json, write_json_file

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




sck = board.GP18
mosi = board.GP19   
miso = board.GP16
cs = digitalio.DigitalInOut(board.GP17)

spi = busio.SPI(sck, mosi, miso)

#mounting SD card
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, '/sd')

def attack_mode():
    #load ducky_script keymap
    dictionary = ducky_script.get_dict()
    #print(dictionary)
    
    #loading json file with active script ID
    active_id = load_json('/sd/active_script.json')['active_script_id']
    #loading active attack script from json file
    active_script = load_json('/sd/scripts.json')[active_id]
    split_script = active_script['script'].split(',')
    #set keyboard
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)

    error = ''
    status = ''
    #Generating HID inputs from ducky script
    try:

        for i in split_script:
            if '+' in i:
                i_split = i.split('+')
                #print(i_split)
                
                for x in i_split:
                    key = dictionary[x]
                    #print(key)
                    
                    kbd.press(key)
                    print('pressing')


                time.sleep(0.2)
                kbd.release_all()
                print('keys released')

            elif '[' and ']' in i:
                layout.write(i[1:-1])
                print('writing')

            elif 'WAIT' in i:
                t = i[4:]
                time.sleep(float(t))

            else:
                key = dictionary[i]
                kbd.send(key)

            status = 'success'

    except:

        error = 'syntax error in script'
        status = 'failed'

    #file = load_json('/data/logs.json')
    #write_json_file('/sd/logs.json', file)
    logs_file = load_json('/sd/logs.json')

    print(active_script['name'])
    log = {
        'status': status,
        'reason': error,
        'script_name': active_script['name']
        }
    
    logs_file['logs'].append(log)
    #logs_file = {'logs': [{'reason': '', 'status': 'success', 'script_name': 'test script'}]}
    write_json_file('/sd/logs.json', logs_file)

    time.sleep(0.5)


def config_mode():

    headers = Headers()
    def open_html(path):
        with open(path) as f:
            return f.read()
        
    network_data = load_json('/sd/network.json')
    wifi.radio.start_ap(ssid=network_data['ssid'], password=network_data['wifi_password'])
    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)
    
    #laoding data from files
    network_file = load_json('/sd/network.json')
    users = load_json('/sd/login.json')

    #page settings on root directory
    @server.route('/', methods=[GET, POST])
    def index(request: Request):
        
        ssid = load_json('/sd/network.json')
        ssid = network_file['ssid']
        wifi_password = network_file['wifi_password']
        login_username = load_json('/sd/login.json')['username']

        #request cookies
        session_ID = request.headers.get('Cookie', '')
        #print(session_ID)

        #session_ID = {'session_ID':'1'}

        message = ''
        if False == bool(session_ID):
            return Redirect(request, '/login')
            pass
        else:
            
            if request.method == 'POST':
                posted_value = request.form_data

                #processing form data 
                data = {key: value for key, value in posted_value.items()}
                print(data)

                login_file = load_json('/sd/login.json')

                #{'login_password': '',
                # 'confirm_password': '', 'ssid': 'test',
                #  'username': 'user', 'wifi_password': '12345678'}

                if data['login_password'] != '':
                    
                    if data['confirm_password'] == data['login_password']:
                        pass
                    else:
                        message = "passwords don't match"
                    
                    
                else:
                    login_file['username'] = data['username']
                    network_file['ssid'] = data['ssid']
                    network_file['wifi_password'] = data['wifi_password']

                    #write user input data to json files
                    write_json_file('/sd/network.json', network_file)
                    write_json_file('/sd/login.json', login_file)

                    #update forms input placeholders
                    message='Settings saved'
                    ssid = load_json('/sd/network.json')
                    ssid = network_file['ssid']
                    wifi_password = network_file['wifi_password']
                    login_username = load_json('/sd/login.json')['username']

            elif request.method == 'GET':
                #print('NOT POST')
                pass
            
            html_page = open_html('/static/settings.html')

            return Response(request, html_page.format(
                ssid_value=(ssid),
                wifi_password_value=(wifi_password),
                login_username=(login_username),
                message=(message)

            ), content_type='text/html')
    
    #page settings on /login directory
    @server.route('/login', methods=[GET, POST])
    def start(request: Request):
        session_ID = request.headers.get('Cookie', '')

        print(session_ID)
        if False == bool(session_ID):
            
            message = ''
            if request.method == 'POST':
                posted_value = request.form_data
                data = {key: value for key, value in posted_value.items()}

                login_file = load_json('/sd/login.json')
                if data['username'] == login_file['username']:
                    if data['password'] == login_file['password']:
                        #cookies = {'session_ID': '1'}

                        headers = Headers()
                        headers.add('Set-Cookie', 'session_ID=1; Path=/')
                        print('headers set')
                        return Redirect(request, '/',headers=headers)
                    else:
                        message = 'wrong username or password'
                        print(message)

                else:
                        message = 'wrong username or password'
                        print(message)

                
            
            html_page = open_html('/static/login.html')
            return Response(request, html_page.format(message=message), content_type='text/html')
        
        else:
            return Redirect(request, '/')

    @server.route('/script_edit', methods=[GET, POST])
    def edit(request: Request):
        #session_ID = request.cookies

        list_output = ''
        script_file = load_json('/sd/scripts.json')
        active_script = load_json('/sd/active_script.json')
        active_script_id = active_script['active_script_id']
        script = ''
        sc_id = ''
        message =''
        script_name = ''

        list_item = open_html('/static/list_item.html')
        for key,value in script_file.items():

            l_item = list_item.format(script_id=key, script_name=value['name'], content_type='text/html')
            list_output = list_output + l_item

        checked = ''
        if request.method == 'GET':

            get = request.query_params

            if len(get) != 0:

                sc_id = get['sc_id']
                print(sc_id)
                print(active_script_id)

                try:

                    script = script_file[sc_id]['script']
                    script_name = script_file[sc_id]['name']
                    if sc_id == active_script_id:
                        checked = 'checked'
                except:
                    pass

        if request.method == 'POST':
            posted_value = request.form_data
            get = request.query_params
            
            if len(get) != 0:

                data = {key: value for key, value in posted_value.items()}
                print(data)
                #print(get['sc_id'])

                if 'delete_script' in data:
                    if data['delete_script'] == 'on':

                        script_file = load_json('/sd/scripts.json')

                        delete_id = str(data['script_id'])

                        if delete_id in script_file:
                            del script_file[delete_id]

                            write_json_file('/sd/scripts.json', script_file)
                        else:
                            print("Script not found")

                        message = 'Script deleted'

                elif 'active_script' in data:
                    if data['active_script'] == 'on':
                        active_script_id = str(data['script_id'])
                        active_script['active_script_id'] = active_script_id
                        #print(active_script)

                        write_json_file('/sd/active_script.json', active_script)
                        message = 'Script saved'

                elif 'new_script' in data:
                    if data['new_script'] == 'on':
                        script_file = load_json('/sd/scripts.json')
                        ids = [int(k) for k in script_file.keys()]
                        new_id = str(max(ids) + 1)

                        #print(type(new_id))
                        script_file[new_id] = {'name': data['name'],
                                               'script': data['script']
                                               }

                        #print(script_file)
                        write_json_file('/sd/scripts.json', script_file)

                        message = 'Script saved'

                        
                script_file = load_json('/sd/scripts.json')
                active_script = load_json('/sd/active_script.json')
                active_script_id = active_script['active_script_id']

                list_output = ''
                list_item = open_html('/static/list_item.html')
                for key,value in script_file.items():

                    l_item = list_item.format(script_id=key, script_name=value['name'], content_type='text/html')
                    list_output = list_output + l_item

        html_page = open_html('/static/script_edit.html')
        return Response(request, html_page.format(
            check=checked,
            script=script,
            list_item=list_output,
            message=message,
            script_name = script_name,
            sc_id = sc_id
            ), content_type='text/html')
    
    #logbook page setup
    @server.route('/logbook', methods=[GET, POST])
    def edit(request: Request):

        html_page = open_html('/static/logbook.html')
        
        log_file = load_json('sd/logs.json')['logs']

        list_item = open_html('/static/log_item.html')
        list_output = ''
        
        id_counter = 0
        for i in log_file:
            print(i)

            
            l_item = list_item.format(id=id_counter, status=i['status'], reason=i['reason'],script_name=i['script_name'], content_type='text/html')
            list_output = list_output + l_item

            id_counter += 1
        
        
        return Response(request, html_page.format(logbook_item=list_output), content_type='text/html')

    server.serve_forever(str(wifi.radio.ipv4_address_ap))


attack = 1
config = 0

button = digitalio.DigitalInOut(board.GP15)
button.switch_to_input(pull=digitalio.Pull.UP)

current_mode = attack
switch_modes = True
last_button_state = button.value
debounce_time = 0.05

while True:
    current = button.value
    
    if current != last_button_state:
        time.sleep(debounce_time)
        
        if button.value == current:

            if last_button_state == True and current == False:

                current_mode = config if current_mode == attack else attack
                switch_modes = True
            
            last_button_state = current

    if switch_modes:
        if current_mode == attack:
            attack_mode()
            
        else:
            config_mode()

        switch_modes = False

    time.sleep(0.01)