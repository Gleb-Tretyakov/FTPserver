import os
import pathlib


class ServerConfig:
    def __init__(self):
        self.host = os.environ.get("HW1_HOST")
        self.port = int(os.environ.get("HW1_PORT"))
        self.mode = os.environ.get("HW1_MODE", "server")
        self.test_type = os.environ.get("HW1_TEST")
        self.quiet = os.environ.get("HW1_QUIET", 0)
        self.directory = os.environ.get("HW1_DIRECTORY")
        self.users = pathlib.Path(os.environ.get("HW1_USERS"))
        self.auth_disabled = os.environ.get("HW1_AUTH_DISABLED", 0)
