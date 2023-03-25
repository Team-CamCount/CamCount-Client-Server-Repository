# Kristian Murphy
# Power saving algorithm with motion detection
# Utilizes deep sleep functionality to power off board when not needed
# Checks camera for motion
# Ultra-lightweight algorithm for averaging camera space and simply checking
# a simple, single integer threshhold
# Processes fast - visualized by the red LED during the processing and the
# flash LED when the camera is active (takes picture, or when it is detecting
# motion)

deepSleepInterval = 2 # seconds
motionThreshhold = 20 # %/256


import uos
import machine
import socket
import ujson
import time
import camera
import network
from time import sleep
import math

# Camera frame dimensions
#HEIGHT = 
#WIDTH = 

# Network SSID and password
SSID = 'SBG6700AC-BF335'
KEY = '629748632e'

# Server socket info
HOST = '192.168.0.17'
PORT = 10000
ADDR = (HOST,PORT)

def connect_to_network():
    sta_if = network.WLAN(network.STA_IF) #Create network variable

    print('Connecting to network...')
    if not sta_if.active():
        sta_if.active(True)
    
    tries = 0
    
    while tries < 3:
        tries += 1
        try:
            time.sleep(2)
            sta_if.connect(SSID, KEY)
            break
        except:
            time.sleep(1)
            print(f'Something went wrong! {sta_if.status()} error!')
        print(sta_if.ifconfig())
    
    return tries

def read_batt():
    raw_voltage = p32.read()
    #raw_voltage = 10 * math.log(3495/(raw_voltage+1))
    disconnected_batt_error = False
    shorted_batt_error = False
	
    if raw_voltage < 500:
        disconnected_batt_error = True
    elif raw_voltage < 6:
        shorted_batt_error = True
	
    battery_percent = (raw_voltage)/4095
    
    print('voltage:', raw_voltage)
    print('battery:', battery_percent) 
    print('shorted battery status:', shorted_batt_error) 
    print('disconnected battery status:', disconnected_batt_error) 

    return [raw_voltage, battery_percent, shorted_batt_error, disconnected_batt_error]


# Function to find mean of pixels in camera buffer data most efficiently
def mean(arr, N):
    
    # Store the average of the array
    avg = 0
 
    # Traverse the array arr[]
    for i in range(N):
         
        # Update avg
        avg += (arr[i] - avg) / (i + 1)
 
    # Return avg
    return round(avg, 6)

    # Set up camera


def state_change():
    firstloop = True
    
    batt_count = 5
    
    cam_id = 'cam1'
    
    while True:
        redLED.value(0) # Turn on red LED

        if firstloop:
            batt_info = read_batt()
            
            client = socket.socket()
            connected = False
            while not connected:
                try:
                    client.connect(ADDR)
                    connected = True
                    print(f'Now connected to {HOST}')
                except:
                    time.sleep(1)
                    
            cam_id = str(cam_id).encode('utf-8')
            client.sendall(cam_id)
            
            id_rec = client.recv(8)
            id_rec = str(id_rec.decode('utf-8'))
            
            if id_rec == 'IDOK':
                print('Server received ID!')
                    
            flashLED.value(1) # Turn on flash LED
        time.sleep(.05) # Brief delay
        buf = camera.capture()
         # Take the picture of current frame and save to buf!
        #time.sleep(.2) # Brief delay
        if firstloop:
            flashLED.value(0) # Turn off flash LED

        #print(buf) # debug buffer

        averageColor = mean(buf, (len(buf)-1))

        print(averageColor) # debug average color

        # Set up variable to save through deep sleep
        rtc = machine.RTC()
        #print(rtc.memory()) # debug
        r = {}
        previousAverageColor = averageColor
        if(rtc.memory()):
            r = ujson.loads(rtc.memory())  # Restore from RTC RAM
            
        print(r) # debug RTC memory result


        if 'previousAverageColor' in r:
            previousAverageColor = r["previousAverageColor"]


        # Do last - since it stores current average color as previous
        if 'bootNum' in r: # Storing boot count to data
            d = {"bootNum": r["bootNum"]+1, "previousAverageColor": averageColor}  # Example data to save
        else:
            d = {"bootNum": 0, "previousAverageColor": averageColor}  # Example data to save
        rtc.memory(ujson.dumps(d))  # Save in RTC RAM
        
        redLED.value(1) # Turn off red LED


        print(abs(averageColor - previousAverageColor))
        if abs(averageColor - previousAverageColor) > 0.5 or firstloop:
            # Flash LED start
            #flashLED.value(1) # Turn on flash LED
            
            # Sending battery info
            batt_count += 1   
            if batt_count > 5:

                print(f'Sending current battery info: {batt_info}...\n')
                batt_msg_ind = str('BATTERY!').encode('utf-8')
                client.sendall(batt_msg_ind)
                
                packed_msg = {'batt': batt_info}
                packed_msg = ujson.dumps(packed_msg)

                packed_msg_len = len(packed_msg)
                packed_msg_len = str(packed_msg_len).encode('utf-8')
                packed_msg_len += b' ' * (8 - len(packed_msg_len))
                    

                client.sendall(packed_msg_len)
                client.sendall(packed_msg)
                batt_count = 0
                #except:
                 #   print('Failed to send battery info!\n')
                
            else:# Sending an image
                try:
                    length = len(buf)
                    len_msg = str(length).encode('utf-8')
                    len_msg += b' ' * (8 - len(len_msg))
                
                    print('Sending image\n')
                    client.sendall(len_msg)
                    client.sendall(buf)
                except:
                    print('Failed to send image!\n')
            
            firstloop = False

        else:
            while True:
                print('Trying to disconnect from server...\n')
                disc_msg = str('BYEBYE').encode('utf-8') #Special disconnect message to end session
                client.sendall(disc_msg)
            
                msg = client.recv(8) #Obtaining the ok from the server to disconnect
                msg = str(msg.decode('utf-8'))
            
                if msg == 'OKOK': 
                    print('Disconnecting from server successfully!')
                    camera.deinit()
                    client.close()
                    machine.deepsleep(2000) # Deep sleep 2s

if __name__ == '__main__':
    #Initializing the camera
    camera.deinit()
    camera.init(0, format=camera.JPEG)
    camera.speffect(camera.EFFECT_BW)
    
    
    #Pin initializations
    p32 = machine.ADC(machine.Pin(32)) #Will need to be changed depending on available pins 
    #p32.atten(machine.ADC.ATTN_11DB) #Range of 3.3V
    redLED = machine.Pin(33,machine.Pin.OUT) # Set up red LED
    flashLED = machine.Pin(4,machine.Pin.OUT) # Set up flash LED

    tries = connect_to_network()
        
    if tries == 3:
        print('Failed to connect to network! Restarting machine...')
        machine.deepsleep(2000)
    else:
        state_change()