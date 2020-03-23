import threading
import socket
import random

from .command_handler import FTPCommandHandler

RECV_LENGTH = 256


class FTPThreadHandler(threading.Thread, FTPCommandHandler):
    def __init__(self, conn, addr, host, port, data_port, directory):
        self.addr = addr
        self.local_address = (host, port)

        threading.Thread.__init__(self)
        FTPCommandHandler.__init__(self, host, data_port, conn, directory)

    def __read_from_socket(self):
        pass

    def run(self):
        from pprint import pprint
        print("self.dict:")
        pprint(self.__dict__)
        if (random.randint(0, 1)):
            self.send_message(120, "Wait a sec")

        self.send_message(220, "Welcome to glebx777 server")
        while not self.quit:
            command = b""
            break_flag = False
            while not b"\r\n" in command:
                cur_command = self.conn.recv(RECV_LENGTH)
                if not cur_command:
                    break_flag = True
                    break
                command += cur_command
            if break_flag:
                break
            command = command.decode("utf-8").strip()
            args = None
            if " " in command:
                command, args = command.split(" ", 1)
            command = command.upper()
            try:
                if command != "USER" and self.not_authorized:
                    self.send_message(530, "Not logged in")
                    continue
                handler_func = getattr(self, command)
                handler_func(args)
                print(f"Get comand {command} from {self.addr}")
            except AttributeError as e:
                print(e)
                self.send_message(500, f"Unknown command {command}")
            except Exception as e:
                print(e)

        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
