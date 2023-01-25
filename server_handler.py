# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 02:39:56 2022

@author: nikit
"""

import socket
import struct
import io
import numpy as np
from PIL import Image
import cv2
import threading


HOST = socket.gethostbyname(socket.gethostname())
PORT = 10000
ADDR = (HOST, PORT)
DISCONNECT = 'BYE BYE!'

def cvt_data_to_img(data):
    load_img = io.BytesIO(data)
    img = np.load(load_img, allow_pickle=True)
    return img
   

def handle_client(conn, addr):
    connected = True
    while connected:
        msg_len = conn.recv(8)
        if msg_len:
            length = msg_len.decode('utf-8')
        
        msg = b''
        while length > 0:
            temp = conn.recv()
            if temp:
               msg += temp
            length -= len(temp)   
                
        img_jpeg = Image.open(io.BytesIO(msg))
        img_np = np.array(img_jpeg)
        
        if bytes == DISCONNECT:
            connected = False
            
    conn.close() 
        
def server_main():
    server.listen()
    
    while True:
        conn, addr = server.accept()
        print(f'New connection established with {addr}!')
        thread = threading.Thread(target=handle_client, args = [conn, addr])
        thread.start()

    
if __name__ == '__main__':
    print('Creating server...')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    
    print('Running server!')
    server_main() 