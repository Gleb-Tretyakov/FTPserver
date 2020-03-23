import socket

from .thread_handler import FTPThreadHandler


class FTPServer:
    def __init__(self, config):
        self.host = config.host
        self.port = int(config.port)
        self.directory = config.directory
        self.auth_disabled = config.auth_disabled

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:
            listen_socket.bind((self.host, self.port))
            listen_socket.listen(5)
            n_threads = 0
            try:
                while(True):
                    (client_connection, address) = listen_socket.accept()
                    handler = FTPThreadHandler(client_connection, address,
                                               self.host, self.port,
                                               self.port + 2 + n_threads,
                                               self.directory)
                    n_threads += 1
                    handler.daemon = True
                    handler.start()
            except KeyboardInterrupt:
                quit()
