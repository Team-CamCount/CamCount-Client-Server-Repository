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
DISCONNECT = str('BYEBYE').encode('utf-8')
BATTERY = str('BATTERY').encode('utf-8')


WEIGHTS = 'C:/Users/nikit/Desktop/YOLOv7/yolov7/yolov7.pt'

def cvt_data_to_img(data):
    load_img = io.BytesIO(data)
    img = np.load(load_img, allow_pickle=True)
    return img

def handle_msg(conn, length):
    msg = b''
    while length > 0:
        temp = conn.recv(length)
        if temp:
            msg += temp
        length -= len(temp)
    
    return msg

def handle_client(conn, addr):
    print(f'New connection established with {addr}!')
    frame_num = 0
    while True:
        init_msg = conn.recv(8)
        print(f'Frame {frame_num+1} received!')
        if init_msg:
            if init_msg == BATTERY:
                batt_len_msg = conn.recv(8)
                batt_info_len = int(batt_len_msg.decode('utf-8'))
                
                batt_info = handle_msg(conn, batt_info_len)
                short_err = 'YES' if batt_info[2] else 'NO'
                disc_err = 'YES' if batt_info[3] else 'NO'
                
                print(f'ESP32-CAM with address {addr} battery info: Voltage = {batt_info[0]}mV, Battery% = {batt_info[1]}%, Short Error = {short_err}, Battery Disconnect = {disc_err}')
                print('Sending battery information to Firebase...')
                #SEND BATTERY INFO TO FIREBASE HERE
                print('Battery info sent to Firebase!')
                continue
            
            elif init_msg == DISCONNECT:
                msg_ok = 'OKOK'
                msg_ok = str(msg_ok).encode('utf-8')
                conn.sendall(msg_ok)
                
                print(f'Client {addr} disconnected!')
                break
            
            else:
                img_len = int(init_msg.decode('utf-8'))
        
        img_msg = handle_msg(conn, img_len)

        img = Image.open(io.BytesIO(img_msg))
        img_np = np.array(img)
        
        #DO DETECTION HERE
        #SEND FLOW DATA TO FIREBASE HERE
        
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