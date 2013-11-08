__author__ = 'brayden'

from Base import BaseWebSocketHandler
import json
import tornado.escape
import base64
from peewee import DoesNotExist
from Minecraft.provision import Bukkit


class CreateServerHandler(BaseWebSocketHandler):
    def open(self):
        self.write_message({"message": "Ready", "success": True})

    def on_message(self, message):
        try:
            message = json.loads(message)  # looks like {"action": "create", "params": {"memory": 512, "address": "192.168.2.3", "port": 25565, "type": "craftbukkit", "build": "latest", "stream": "rb"}, "authentication": "<cookie value>"}
            session = tornado.escape.url_unescape(message['authentication'])
            auth = False
            username = None
            if len(session.split('|')) == 2:
                username = (base64.decodestring(session.split('|')[0])).strip()
                hash = session.split('|')[1]
                try:
                    if self.application.check_session(username, hash):
                        if self.application.db.isUserAdmin(username):
                            auth = True  # so much nesting!
                        else:
                            self.write_message({"success": False, "message": "Required permissions not present."})
                    else:
                        self.write_message({"success": False, "message": "Bad authentication."})
                except DoesNotExist:
                    self.write_message({'success': False, "message": "Bad authentication."})
            else:
                self.write_message({'success': False, "message": "Bad authentication"})

            if message['action'] == "create" and auth:
                username = username
                memory = message['params']['memory']
                address = message['params']['address']
                port = message['params']['port']
                server_type = message['params']['type']
                if not self.application.db.isAddressTaken(address, port):
                    self.application.db.addServer(address, port, memory, username, server_type=server_type)
                    self.write_message({"success": True, "message": "Added server to database."})
                    server_id = self.application.db.getServerID(address, port)
                    self.server_id = server_id
                    self.write_message({"success": True, "message": "Verified database entry, got ID %s" % server_id})
                    if server_type == "craftbukkit":
                        self.write_message({"message": "entered bukkit", "success": True})
                        Bukkit().install(self, **message['params'])
                    else:
                        self.write_message({"success": False, "message": "Type not implemented."})
                else:
                    self.write_message({"success": False, "message": "IP/Port combination already taken."})
            else:
                self.write_message({"success": False, "message": "Unrecognised action."})

        except ValueError or KeyError:
            self.write_message({"success": False, "message": "Not well formatted message."})