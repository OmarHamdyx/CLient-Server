import os
import socket
import sys
import base64


def read_input_file(filename):
    try:
        with open(filename) as file:
            filedata = file.read()
            filedata = filedata.splitlines()
        return filedata

    except IOError:
        print("file not found")
        return None


def retrieve_file_contents(filename):
    try:
        path = os.getcwd() + "\client" + filename
        with open(path) as file:
            filedata = file.read()
        return filedata

    except IOError:
        print("requested file to upload doesn't exist")
        return


def parse_operation(operation):
    operation = operation.split()
    command = operation[0]
    filename = operation[1]
    host_name = operation[2]
    if len(operation) == 4:
        port_number = operation[3]
    else:
        port_number = "80"

    packet = ""

    if command.lower() == 'get':
        packet = packet + "GET " + filename + " HTTP/1.1" + "\r\n" + "HOST:" + host_name + ":" + port_number + "\r\n\r\n"
    elif command.lower() == 'post':
        filedata = retrieve_file_contents(filename)
        if not filedata:
            filename = None
            return host_name, port_number, command, filename, packet
        packet = packet + "POST " + filename + " HTTP/1.1" + "\r\n" + "HOST:" + host_name + ":" + port_number + "\r\n\r\n" + filedata + "\r\n"
    else:
        print("command not recognized")
    return host_name, port_number, command, filename, packet


if __name__ == '__main__':
    cache = {}
    filename = "input_file.txt"
    operations = read_input_file(filename)
    if operations == None:
        sys.exit()
    for operation in operations:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            host_name, port_number, command, filename, packet = parse_operation(operation)
            
            if not filename:
                continue
            if command.lower() != 'get' and command.lower() != 'post':
                continue
            if packet in cache:
                print(cache.get(packet))
                continue
            s.connect((host_name, int(port_number)))
            s.sendall(packet.encode('ascii'))
            data = s.recv(500000)
            data = data.decode('ascii')
            print(data)
            cache[packet] = data
            if command.lower() == 'get':
                status = data.split()
                if status[1] != '200':
                    continue
                filename = filename.split('/')
                filename = filename[-1]
                extension = filename.split(".")
                extension = extension[-1]
                path = os.getcwd() + "\client\\" + filename
                if extension == "txt":
                    with open(path, "w") as file:
                        data = data.split("\r\n\r\n")
                        data = data[1].replace("\r\n", '')
                        file.write(data)
                elif extension == "png":
                    with open(path, "wb") as file:
                        data = data.split("\r\n\r\n")
                        data = data[1].replace("\r\n", '')
                        data = data.encode("utf-8")
                        file.write(base64.b64decode((data)))
                elif extension == "html":
                    with open(path, "w") as file:
                        data = data.split("\r\n\r\n")
                        data = data[1].replace("\r\n", '')
                        file.write(data)
