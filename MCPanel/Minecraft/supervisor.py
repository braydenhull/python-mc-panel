__author__ = 'brayden'

import xmlrpclib


class Supervisor:
    def __init__(self, username, password):
        self.server = xmlrpclib.Server('http://%s:%s@127.0.0.1:9001/RPC2' % (username, password))

    def is_process_running(self, server_id):
        state = self.server.supervisor.getProcessInfo(server_id)['statename']
        if state == "RUNNING":
            return True
        else:
            return False

    def run_command(self, server_id, command):
        return self.server.supervisor.sendProcessStdin(server_id, command)

    def get_pid(self, server_id):
        return self.server.supervisor.getProcessInfo(server_id)['pid']