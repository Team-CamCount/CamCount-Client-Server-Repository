import numpy as np
import io
import uasyncio as asyncio
import time
import camera
import socket
import machine
import sys
import struct


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

#=====================================================================================================
#Code temporarily borrowed from http://stupidpythonideas.blogspot.com/2013/05/sockets-are-byte-streams-not-message.html

def send_one_message(client, data):
    length = len(data)
    client.sendall(struct.pack('!I', length))
    client.sendall(data)

#=====================================================================================================

def send_img(host, port):
    client = socket.socket()
    client.connect((host, port))
    print('Connected to server!\n')
    send_tries = 0
    cap_tries = 0
    
    while send_tries < 10 and cap_tries < 5:
        try:
            time.sleep(0.05)
            buf = camera.capture()
        except:
            print('Failed to capture image!\n')
            cap_tries += 1
        try:
            length = len(buf)
            len_msg = str(length).encode('utf-8')
            len_msg += b' ' * (8 - len(len_msg))
            
            print('Sending image\n')
            client.sendall(len_msg)
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
            
            camera.init(0, format=camera.JPEG, quality=10)
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
    
    SSID = ''
    KEY = ''
    
    HOST = '192.168.0.17'
    PORT = 10000
    
    comm_with_server(HOST, PORT, SSID, KEY)