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

import argparse
import time
from pathlib import Path

import cv2
#import torch
#import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

HOST = socket.gethostbyname(socket.gethostname())
PORT = 10000
ADDR = (HOST, PORT)
DISCONNECT = 'BYE BYE!'
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
        if msg_len:
            length = int(msg_len.decode('utf-8'))
        
        msg = b''
        while length > 0:
            temp = conn.recv(length)
            if temp:
               msg += temp
            length -= len(temp)  

        print('Obtained new image!')        
        
        if msg == DISCONNECT:
            print('Client {addr} disconnected!')
            break

        img = Image.open(io.BytesIO(msg))
        img_np = np.array(img)
        
        frame_num += 1 
        #detect(source=img_jpeg)
        cv2.imwrite(f'C:/Users/nikit/Desktop/ESP32-Images/IMG{frame_num}.jpg', img_np)
        print('Saved new image!')
       
    conn.close() 
        
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