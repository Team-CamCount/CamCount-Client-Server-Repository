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


HOST = '192.168.0.17'
PORT = 10000

def cvt_data_to_img(data):
    load_img = io.BytesIO(data)
    img = np.load(load_img, allow_pickle=True)
    return img
   
#=====================================================================================================
#Code temporarily borrowed from http://stupidpythonideas.blogspot.com/2013/05/sockets-are-byte-streams-not-message.html

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
    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f'Now connected to {addr}!')
    print(addr)

    tries = 0
    friends = []
    video_arr = []
    
    while tries < 100:
        data_array = bytearray()
        chunks = 0
        
        img_b = recv_one_message(conn)
        image = Image.open(io.BytesIO(img_b))
        img = np.array(image)
        
        video_arr.append(img)
        print('Left inner loop!')
        
        tries += 1
    
    height, width, _ = video_arr[1].shape
    
    video = cv2.VideoWriter('video.avi', -1, 1, (width, height))
    
    for image in video_arr:
        video.write(image)
        
    cv2.destroyAllWindows()
    video.release()
    
        
        
       #try:

           #image.show()
        #except:
          #print('Failed to display image, an error occured in sending the image!')  
        

            
        
        