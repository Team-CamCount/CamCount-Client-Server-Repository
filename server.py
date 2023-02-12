# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 02:39:56 2022

@author: nikit
"""

import socket
import io
import numpy as np
from PIL import Image
import threading
import time


from pathlib import Path

import cv2

HOST = socket.gethostbyname(socket.gethostname())
PORT = 10000
ADDR = (HOST, PORT)
DISCONNECT = str('293293').encode('utf-8')
WEIGHTS = 'C:/Users/nikit/Desktop/YOLOv7/yolov7/yolov7.pt'

def cvt_data_to_img(data):
    load_img = io.BytesIO(data)
    img = np.load(load_img, allow_pickle=True)
    return img

def handle_client(conn, addr):
    print(f'New connection established with {addr}!')
    frame_num = 0
    
    while True:
        msg_len = conn.recv(8)
        print(msg_len)
        if msg_len:
            if msg_len == DISCONNECT:
                msg_ok = '6565'
                msg_ok = str(msg_ok).encode('utf-8')
                conn.sendall(msg_ok)
                
                print(f'Client {addr} disconnected!')
                break               
            length = int(msg_len.decode('utf-8'))
            length = int(length)
        
        msg = b''
        while length > 0:
            temp = conn.recv(length)
            if temp:
               msg += temp
            length -= len(temp)  

        img = Image.open(io.BytesIO(msg))
        img_np = np.array(img)
        
        frame_num += 1 
        #detect(source=img_jpeg)
        cv2.imwrite(f'C:/Users/nikit/Desktop/ESP32-Images/IMG{frame_num}.jpg', img_np)
        #print('Saved new image!')

    conn.close() 
    return
        
def server_main():
    server.listen()
    
    while True:
        conn, addr = server.accept()

        thread = threading.Thread(target=handle_client, args = [conn, addr])
        thread.start()

    
if __name__ == '__main__':
    print('Creating server...')
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    
    print('Running server!')
    server_main() 