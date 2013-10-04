__author__ = 'brayden'

import socket


class ShortStatus:
    def __init__(self, address, port, timeout=2):
        self.address = address
        self.port = port
        self.timeout = timeout

    def get(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.address, self.port))
        except socket.error as exception:
            raise StatusError(exception)
        s.settimeout(self.timeout)
        s.send('\xfe\x01')
        data = s.recv(1024)
        s.close()
        data = data[3:].decode('utf-16be').split('\x00')
        return data[1:]


class StatusError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)