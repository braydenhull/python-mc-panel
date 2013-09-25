__author__ = 'brayden'

import xmlrpclib


class Supervisor:
    def __init__(self, username, password):
        self.server = xmlrpclib.Server('http://%s:%s@127.0.0.1:9001/RPC2' % (username, password))

    def isProcessRunning(self, server_id):
        state = self.server.supervisor.getProcessInfo('minecraft_' + str(server_id))['statename']
        if state == "RUNNING":
            return True
        else:
            return False

    def runCommand(self, server_id, command):
        return self.server.supervisor.sendProcessStdin('minecraft_' + str(server_id), command)