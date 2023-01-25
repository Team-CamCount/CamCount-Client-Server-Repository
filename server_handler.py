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
   
#=====================================================================================================
#Code borrowed from http://stupidpythonideas.blogspot.com/2013/05/sockets-are-byte-streams-not-message.html

def recv_one_message(conn):
    lengthbuf = recvall(conn, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(conn, length)

def recvall(conn, count):
    buf = b''
    while count:
        newbuf = conn.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

#=====================================================================================================

def handle_client(conn, addr):
    connected = True
    while connected:
        bytes = recv_one_message(conn) 
        img_jpeg = Image.open(io.BytesIO(bytes))
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