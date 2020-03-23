import socket

BUFFER = 1024
CRLF = "\r\n"


def send_request(sock, req):
    sock.send((req + CRLF).encode("utf-8"))
    data = sock.recv(BUFFER)
    data = data.strip().decode("utf-8")
    return data.split(" ", 1)


def send_slow_request(sock, req):
    sock.send((req).encode("utf-8"))
    sock.send((CRLF).encode("utf-8"))
    data = sock.recv(BUFFER)
    data = data.strip().decode("utf-8")
    return data.split(" ", 1)


def minimal_test(config):
    flag = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.host, config.port))
    data = s.recv(BUFFER)
    data = data.strip().decode("utf-8")
    parts = data.split(" ", 1)
    if len(parts) != 2:
        flag = False
        return flag
    # If 120
    if parts[0][0] == '1':
        data = s.recv(BUFFER)
        data = data.strip().decode("utf-8")

    parts = send_request(s, "USER a")
    flag = flag and (parts[0][0] == '2')

    for com in ["TYPE", "MOde", "STRU"]:
        parts = send_request(s, com)
        flag = flag and (parts[0][0] == '5')

    for com in ["QUIT s", "NOOP sd"]:
        parts = send_request(s, com)
        flag = flag and (parts[0][0] == '5')

    for com in ["NOOP"]:
        parts = send_request(s, com)
        flag = flag and (parts[0][0] == '2')

    for com in ["TYPE", "MOde", "STRU"]:
        parts = send_slow_request(s, com)
        flag = flag and (parts[0][0] == '5')

    for com in ["QUIT"]:
        parts = send_request(s, com)
        flag = flag and (parts[0][0] == '2')

    s.close()
    return flag


test_handlers = {
    "minimal": minimal_test
}


def do_tests(config):
    test = config.test_type

    if test in test_handlers:
        try:
            flag = test_handlers[test](config)
        except Exception:
            flag = False

        if flag:
            print("ok")
        else:
            print("fail")
