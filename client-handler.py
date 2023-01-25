import time
import camera
import socket
import machine


def connect_to_network(ssid, key):
    import network
    sta_if = network.WLAN(network.STA_IF)

    print('Connecting to network...')
    sta_if.active(True)
    try:
        sta_if.connect(ssid, key)
    except:
        print('Something went wrong! Could not connect to network, check SSID and Key.')
    print(sta_if.ifconfig())

def send_img(host, port):
    client = socket.socket()
    client.connect((host, port))
    
    send_tries = 0
    cap_tries = 0
    
    while send_tries < 10 and cap_tries < 5:
        try:
            time.sleep(0.1)
            buf = camera.capture()
        except:
            print('Failed to capture image!\n')
            cap_tries += 1
        try:
            client.sendall(len(buf).encode('utf-8'))
            client.sendall(buf)
        except:
            print('Failed to send image!\n')
            send_tries += 1
    if cap_tries >= 5:
        print('There is an issue with a camera, restarting the program to try again!')
    if send_tries >= 10:
        print('There is an issue with connecting to the server, restarting the program to try again!')
    client.close()
    return

def comm_with_server(host, port, ssid, key):
    tries = 0
    
    led = machine.Pin(4, machine.Pin.OUT)
    led.off()

    
    while tries < 3:
        tries += 1 
        try:
            camera.deinit()
            time.sleep(1)
            
            camera.init(0, format=camera.JPEG, quality=30)
            camera.speffect(camera.EFFECT_BW)
            time.sleep(2)
            
            connect_to_network(ssid, key)
            send_img(host, port)
            
            camera.deinit() 
        except:
            print('Something went wrong! Trying again in 5 seconds...\n')
            time.sleep(5)
          
    #last ditch effort to scream for help
    #while True:
        #for i in range(0,3):
            #led.on()
            #time.sleep(1)
            #led.off()
        #time.sleep(3)
            

if __name__ == '__main__':
    
    SSID = 'SBG6700AC-BF335'
    KEY = '629748632e'
    
    HOST = '192.168.0.17'
    PORT = 10000
    
    comm_with_server(HOST, PORT, SSID, KEY)