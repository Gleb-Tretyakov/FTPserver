import os
import socket
from enum import Enum


class ETransferMode(Enum):
    STREAM = 1


class ERepresentationType(Enum):
    ASCII_NON_PRINT = 1


class EStructureType(Enum):
    FILE = 1
    RECORD = 2


BUFFER_SIZE = 1024


class FTPCommandHandler:
    def __init__(self, host, data_port, conn, directory):
        self.quit = False
        self.conn = conn
        self.transfer_mode = ETransferMode.STREAM
        self.type = ERepresentationType.ASCII_NON_PRINT
        self.struct = EStructureType.FILE
        self.data_socket = None
        self.work_dir = directory
        self.not_authorized = True
        self.pasv_mode = False
        self.pasv_socket = None
        self.data_host = host
        self.data_port = data_port

    def check_data_socket(f):
        def wrapped(*args, **kwargs):
            print(*args)
            if args[0].data_socket:
                return f(*args, **kwargs)
            else:
                args[0].send_message(425, "Open data connection firstly by PORT or PASV")

        return wrapped

    def check_second_argument(f):
        def wrapped(*args, **kwargs):
            print(*args)
            if args[1]:
                return f(*args, **kwargs)
            else:
                args[0].send_message(500, "Command needs an argument ")

        return wrapped

    def get_server_path(self, filename):
        return os.path.normpath(os.path.join(self.work_dir, filename))

    def open_data_socket(self, data_host, data_port):
        try:
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.pasv_mode:
                self.data_socket, _ = self.pasv_socket.accept()
                pass
            else:
                self.data_socket.connect((data_host, data_port))
            return True
        except Exception as e:
            print(f"Cannot open data connect for {data_host} {data_port}: {e}")
            return False

    def close_data_socket(self):
        try:
            self.data_socket.close()
            self.data_socket = None
            if self.pasv_mode:
                self.pasv_socket.close()
        except Exception as e:
            print(e)

    def send_message(self, code, message):
        return self.conn.send(f'{code} {message}\r\n'.encode("utf-8"))

    def send_data(self, data):
        return self.data_socket.send(data.encode("utf-8"))

    def read_data(self):
        return self.data_socket.recv(BUFFER_SIZE).decode("utf-8")

    @check_second_argument
    def USER(self, arg):
        self.send_message(230, "User logged in")
        self.not_authorized = False

    @check_second_argument
    def PORT(self, arg):
        bytes = arg.split(",")
        if len(bytes) != 6:
            self.send_message(501, "Bad format")
        elif any(list(map(lambda x: not (x.isdigit() and int(x) >= 0 and int(x) < 256), bytes))):
            self.send_message(501, "Bad byte form")
        else:
            data_host = '.'.join(bytes[:4])
            data_port = (int(bytes[4]) << 8) + int(bytes[5])
            if self.pasv_mode:
                self.pasv_mode = False
                self.pasv_socket.close()

            if self.open_data_socket(data_host, data_port):
                self.send_message(200, "OK")
            else:
                self.send_message(500, "Could not connect")

    @check_data_socket
    @check_second_argument
    def RETR(self, filename):
        filename = self.get_server_path(filename)
        if not os.path.exists(filename):
            self.send_message(550, "File unavailable")
        else:
            self.send_message(150, "Opening data connection")
            result = False
            try:
                with open(filename, 'r') as file:
                    while True:
                        data = file.read(BUFFER_SIZE)
                        if not data:
                            result = True
                            break
                        self.send_data(data)

            except Exception as e:
                self.send_message(451, "Local error")
                print('RETR', e)
            if result:
                self.send_message(226, "Successfully transfered")
            self.close_data_socket()

    @check_data_socket
    @check_second_argument
    def STOR(self, filename):
        filename = self.get_server_path(filename)
        self.send_message(150, "Opening data connection")
        result = False
        try:
            with open(filename, 'w') as file:
                while True:
                    data = self.read_data()
                    print(data)
                    if not data:
                        result = True
                        break
                    file.write(data)

        except Exception as e:
            self.send_message(451, "Local error")
            print('STOR', e)
        if result:
            self.send_message(226, "Successfully transfered")
        self.close_data_socket()

    @check_second_argument
    def STRU(self, struct_type):
        struct_type = struct_type.upper()
        if struct_type == "F":
            self.struct = EStructureType.FILE
            self.send_message(200, "OK. Structur type set to F")
        elif struct_type == "R":
            self.send_message(504, "Not OK")
        else:
            self.send_message(500, "Unknown")

    @check_second_argument
    def MODE(self, mode):
        mode = mode.upper()
        if mode == "S":
            self.transfer_mode = ETransferMode.STREAM
            self.send_message(200, "OK. Transer mode set to S")
        else:
            self.send_message(500, "Unknown transer mode")

    @check_second_argument
    def TYPE(self, type):
        type = type.upper()
        if type == "AN":
            self.type = ERepresentationType.ASCII_NON_PRINT
            self.send_message(200, "OK. Representation type set to AN")
        else:
            self.send_message(500, "Unknown representation type")

    def NOOP(self, arg):
        if arg:
            self.send_message(500, "Command does not accept arguments")
        else:
            self.send_message(200, "OK")

    def QUIT(self, arg):
        if arg:
            self.send_message(500, "Command does not accept arguments")
        else:
            self.send_message(221, "Bye bye")
            self.quit = True

    def PASV(self, arg):
        self.pasv_mode = True
        self.pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pasv_socket.bind((self.data_host, self.data_port))
        self.pasv_socket.listen(5)

        self.send_message(227, "Entering passive mode")
