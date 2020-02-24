from config import ServerConfig

from src.server import FTPServer
from tests.tests import do_tests


def main():
    config = ServerConfig()
    if config.mode == "server":
        with open(config.users, "r") as f:
            data = [item.strip().split("\t") for item in f.readlines()]
            print(data)
            FTPServer(config).run()
        pass
    elif config.mode == "tests":
        do_tests(config)


if __name__ == "__main__":
    main()
