

import socket
from _thread import *
import threading
import os
import time
import base64
from time import sleep
timeout=0
timedout=False

def parse_request(data,conn):
    request = data.decode('ascii')
    print(request)
    request_get = request.split()
    command = request_get[0]
    filename = request_get[1]
    if command == 'GET':
        extension = filename.split(".")
        extension = extension[-1]
        if extension == "txt":
            try:
                path = os.getcwd() + "\server" + filename
                with open(path) as file:
                    filedata = file.read()
                    packet= "HTTP/1.1 200 OK\r\n\r\n" + filedata + "\r\n"
                    conn.sendall(packet.encode('ascii'))

            except IOError:
                conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode('ascii'))
        elif extension == "png":
            try:
                path = os.getcwd() + "\server" + filename
                with open(path, 'rb') as file:
                    filedata = base64.b64encode(file.read())

                    packet =  "HTTP/1.1 200 OK\r\n\r\n" + filedata.decode("utf-8") + "\r\n"
                    conn.sendall(packet.encode('ascii'))

            except IOError:
                conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode('ascii'))
        elif extension == "html":
            try:
                path = os.getcwd() + "\server" + filename
                with open(path) as file:
                    filedata = file.read()

                    packet = "HTTP/1.1 200 OK\r\n\r\n" + filedata + "\r\n"
                    conn.sendall(packet.encode('ascii'))


            except IOError:
                conn.send("HTTP/1.1 404 Not Found\r\n\r\n".encode('ascii'))




    elif command == 'POST':
        conn.send("HTTP/1.1 200 OK\r\n\r\n".encode('ascii'))
        path = os.getcwd() + "\server" + filename
        with open(path, "w") as file:
            request = request.split("\r\n\r\n")
            filedata = request[-1]
            filedata = filedata.replace("\r\n", '')
            file.write(filedata)


def pipelined_thread(conn):
    global timeout,timedout
    try:
        conn.setblocking(False)
        data = conn.recv(1024)
        if data:
            start_new_thread(pipelined_thread, (conn,))
            parse_request(data, conn)
            timeout = time.time() + 3


    except:
        print("connection closed by main thread")



def connection_thread(conn):
    global timeout,timedout
    data = conn.recv(1024)
    start_new_thread(pipelined_thread, (conn,))
    #parse request:
    parse_request(data,conn)

    timeout = time.time() + 3
    while True:
        if time.time() > timeout:

            timedout=True

            print("main thread timeout!")
            break

    conn.close()






if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print("socket binded to port", PORT)
    print("socket is listening")
    while True:
        s.listen()

        conn, addr = s.accept()



        print('Connected to :', addr[0], ':', addr[1])


        start_new_thread(connection_thread, (conn,))



    #s.close()

