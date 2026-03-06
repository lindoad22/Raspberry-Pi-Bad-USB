import time
import usb_hid
import wifi
import socketpool
import ducky_script
from fce import load_json, write_json_file, write_to_csv, read_csv_logs, open_html

from adafruit_hid.keyboard import Keyboard
from layout_cz import KeyboardLayout
from adafruit_hid.keycode import Keycode

import adafruit_httpserver
from adafruit_httpserver import GET,POST, Request, Response, Server, Headers, Redirect, NOT_FOUND_404, MOVED_PERMANENTLY_301

def attack_mode():
    #load ducky_script keymap
    dictionary = ducky_script.get_dict()
    
    #loading json file with active script ID
    active_id = load_json('/sd/active_script.json')['active_script_id']
    #loading active attack script from json file
    active_script = load_json('/sd/scripts.json')[active_id]
    split_script = active_script['script'].split(';;')
    #set keyboard
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayout(kbd)

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
                    #print('pressing')


                time.sleep(0.2)
                kbd.release_all()
                #print('keys released')

            elif i.startswith('TEXT '):
                layout.write(i[5:])
                #print('writing')

            elif i.startswith('WAIT '):
                t = i[5:]
                time.sleep(float(t))

            else:
                key = dictionary[i]
                kbd.send(key)

            status = 'success'
            error = 'none'

    except:

        kbd.release_all()
        error = 'syntax error in script'
        status = 'failed'

    write_to_csv('/sd/logs.csv', status, error, active_script['name'])


def config_mode():
    global server, pool
    headers = Headers()
        
    network_file = load_json('/sd/network.json')
    login_file = load_json('/sd/login.json')
    wifi.radio.start_ap(ssid=network_file['ssid'], password=network_file['wifi_password'])
    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static", debug=True)

    
    #page settings on root directory
    @server.route('/', methods=[GET, POST])
    def index(request: Request):
        
        #print("Request received at /")
        ssid = network_file['ssid']
        wifi_password = network_file['wifi_password']

        login_username = login_file['username']

        #request cookies
        cookie_header = request.headers.get('Cookie', '')
        #print(cookie_header)

        message = ''
        if "session_ID=1" not in cookie_header:
            #print('No valid session, redirecting to login')
            return Redirect(request, '/login')         
        else:

            if request.method == 'POST':
                posted_value = request.form_data

                #processing form data 
                data = {key: value for key, value in posted_value.items()}

                if data['login_password'] != '':
                    if data['confirm_password'] == data['login_password']:
                        login_file['password'] = data['login_password']
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
                    ssid = data['ssid']
                    wifi_password = data['wifi_password']
                    login_username = data['username']

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

        if False == bool(session_ID):
            
            message = ''
            if request.method == 'POST':
                posted_value = request.form_data
                data = {key: value for key, value in posted_value.items()}

                if data['username'] == login_file['username']:
                    if data['password'] == login_file['password']:

                        headers = Headers()
                        headers.add('Set-Cookie', 'session_ID=1; Path=/')
                        #print('headers set')
                        return Redirect(request, '/',headers=headers)
                    else:
                        message = 'wrong username or password'
                        #print(message)

                else:
                        message = 'wrong username or password'
                        #print(message)

                
            
            html_page = open_html('/static/login.html')
            return Response(request, html_page.format(message=message), content_type='text/html')
        
        else:
            #Valid session, redirecting to settings
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


                if 'delete_script' in data:
                    if data['delete_script'] == 'on':

                        script_file = load_json('/sd/scripts.json')

                        delete_id = str(data['script_id'])

                        if delete_id in script_file:
                            del script_file[delete_id]

                            write_json_file('/sd/scripts.json', script_file)
                        else:
                            message = 'Script not found'

                        message = 'Script deleted'

                elif 'active_script' in data:
                    if data['active_script'] == 'on':
                        active_script_id = str(data['script_id'])
                        active_script['active_script_id'] = active_script_id

                        write_json_file('/sd/active_script.json', active_script)

                        script_id = data['script_id']
                        script_file[script_id] = {'name': data['name'],
                                            'script': data['script']
                                            }

                        write_json_file('/sd/scripts.json', script_file)

                        message = 'Script saved'

                elif 'new_script' in data:
                    if data['new_script'] == 'on':
                        script_file = load_json('/sd/scripts.json')
                        ids = [int(k) for k in script_file.keys()]
                        new_id = str(max(ids) + 1)

                        script_file[new_id] = {'name': data['name'],
                                               'script': data['script']
                                               }

                        write_json_file('/sd/scripts.json', script_file)

                        message = 'Script saved'
                else:
                    
                    script_id = str(data['script_id'])
                    script_file[script_id] = {'name': data['name'],
                                            'script': data['script']
                                            }


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
        
        log_file = read_csv_logs('sd/logs.csv')
        log_file.reverse()
        list_item = open_html('/static/log_item.html')
        list_output = ''
        
        id_counter = len(log_file) - 1
        for i in log_file:

            
            l_item = list_item.format(id=id_counter, status=i['status'], error=i['error'],script_name=i['script_name'], content_type='text/html')
            list_output = list_output + l_item

            id_counter -= 1
        
        
        return Response(request, html_page.format(logbook_item=list_output), content_type='text/html')

    server.start(str(wifi.radio.ipv4_address_ap))


def stop_server():
    global server, pool
    if server == None:
        return
    else:
        try:
            server.stop()
            pool.close()

            pool = None
            server = None
        except:
            pass   

def check_server():
    global server, pool

    if server == None:
        return
    else:
        server.poll()