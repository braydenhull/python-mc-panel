__author__ = 'brayden'

from Base import BaseWebSocketHandler
import json
import tornado.escape
from peewee import DoesNotExist
from Minecraft.provision import Bukkit
from Minecraft.provision import Vanilla


class CreateServerHandler(BaseWebSocketHandler):
    def open(self):
        self.write_message({"message": "Ready", "success": True, "complete": False})

    def on_message(self, message):
        try:
            message = json.loads(message)
            # looks like {"params": {"memory": 512, "address": "192.168.2.3", "port": 25565, "type": "craftbukkit", "build": "latest", "stream": "rb"}, "authentication": "<cookie value>", "owner": "<owner, str>"}
            session = tornado.escape.url_unescape(message['authentication'])
            auth = False
            username = None
            if len(session.split('|')) == 2:
                username = (((session.split('|')[0])).decode('hex').decode('utf-8')).strip()
                hash = session.split('|')[1]
                try:
                    if self.application.check_session(username, hash):
                        if self.application.db.is_user_admin(username):
                            auth = True  # so much nesting!
                        else:
                            self.write_message({"success": False, "message": "Required permissions not present.", "complete": False})
                    else:
                        self.write_message({"success": False, "message": "Bad authentication.", "complete": False})
                except DoesNotExist:
                    self.write_message({'success': False, "message": "Bad authentication.", "complete": False})
            else:
                self.write_message({'success': False, "message": "Bad authentication", "complete": False})

            if auth:
                memory = message['params']['memory']
                address = message['params']['address']
                port = message['params']['port']
                server_type = message['params']['type']
                owner = message['owner']
                stream = message['params']['stream']
                if not self.application.db.is_address_taken(address, port):
                    self.application.db.add_server(address, port, memory, owner, stream, server_type=server_type)
                    self.write_message({"success": True, "message": "Added server to database.", "complete": False})
                    server_id = self.application.db.get_server_id(address, port)
                    self.server_id = server_id
                    self.write_message({"success": True, "message": "Verified database entry, got ID %s" % server_id, "complete": False})
                    if server_type == "craftbukkit":
                        Bukkit().install(self, **message['params'])
                    elif server_type == "vanilla":
                        Vanilla().install(self, use_websocket=True,**message['params'])
                    else:
                        self.write_message({"success": False, "message": "Type not implemented.", "complete": False})
                else:
                    self.write_message({"success": False, "message": "IP/Port combination already taken.", "complete": False})
        except ValueError or KeyError:
            print message
            self.write_message({"success": False, "message": "Not well formatted message.", "complete": False})