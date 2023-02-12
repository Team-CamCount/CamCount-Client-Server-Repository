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

# Camera frame dimensions
HEIGHT = 160
WIDTH = 160

#Network SSID and password
SSID = 'SBG6700AC-BF335'
KEY = '629748632e'

#Server socket info
HOST = '192.168.0.17'
PORT = 10000
DISCONNECT = 'BYE BYE!'.encode('utf-8')

def connect_to_network():
    import network
    sta_if = network.WLAN(network.STA_IF) #Create network variable

    print('Connecting to network...')
    if not sta_if.active():
        sta_if.active(True)
    
    try:
        sta_if.connect(SSID, KEY)
    except:
        print(f'Something went wrong! {sta_if.status()} error!')
    print(sta_if.ifconfig())

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
    while True:
        redLED.value(0) # Turn on red LED

        if firstloop:
            client = socket.socket()
            client.connect((HOST, PORT))
            flashLED.value(1) # Turn on flash LED
        time.sleep(.2) # Brief delay

        buf = camera.capture() # Take the picture of current frame and save to buf!
        time.sleep(.2) # Brief delay
        
        if firstloop:
            flashLED.value(0) # Turn off flash LED

        #print(buf) # debug buffer

        averageColor = mean(buf, (WIDTH*HEIGHT))

        #print(averageColor) # debug average color

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
        if abs(averageColor - previousAverageColor) > 20:
            # Flash LED start
            flashLED.value(1) # Turn on flash LED

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
            camera.deinit()
            client.sendall(DISCONNECT)
            client.close()
            machine.deepsleep(2000) # Deep sleep 2s

if __name__ == '__main__':
    camera.init(0, format=camera.GRAYSCALE, framesize=camera.FRAME_QQVGA, fb_location=camera.PSRAM)

    # LED assignments
    redLED = machine.Pin(33,machine.Pin.OUT) # Set up red LED
    flashLED = machine.Pin(4,machine.Pin.OUT) # Set up flash LED

    tries = 0

    while tries < 3:
        try:
            connect_to_network()
        except:
            tries += 1
            print(f'Failed on try {tries}, there are {3 - tries} tries left!')
        
    if tries == 3:
        print('Failed to connect to network! Restarting machine...')
        machine.deepsleep(2000)
    else:
        state_change()