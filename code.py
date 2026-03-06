import time
from modes import attack_mode, config_mode, check_server, stop_server

#sd card imports
import adafruit_sdcard
import busio
import digitalio
import board
import storage

sck = board.GP18
mosi = board.GP19 #TX  
miso = board.GP16# RX
cs = digitalio.DigitalInOut(board.GP17)

spi = busio.SPI(sck, mosi, miso)

sdcard = adafruit_sdcard.SDCard(spi, cs, baudrate=1000000) # 1MHz
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

attack = 1
config = 0

button = digitalio.DigitalInOut(board.GP15)
button.switch_to_input(pull=digitalio.Pull.UP)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

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
            
            try:
                stop_server()
            except:
                pass

            #print("Switched to attack mode")
            led.value = False
            #attack_mode()

        else:
            #print("Switched to config mode")
            led.value = True
            config_mode()
            

        switch_modes = False

    if current_mode == config:

        try:
            check_server()
        except:
            pass

    time.sleep(0.1)
