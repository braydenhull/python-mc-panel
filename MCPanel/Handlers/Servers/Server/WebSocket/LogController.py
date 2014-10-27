__author__ = 'brayden'

from . import BaseServerWebSocketHandler
import json
from peewee import DoesNotExist
import tornado.escape
import os
import subprocess
import tornado.ioloop

class GetLog(BaseServerWebSocketHandler):
    def open(self, server_id):
        self.server_id = server_id
        self.auth = False

    def on_message(self, message):
        try:
            message = json.loads(message)
            username = None
            if message['action'] == "auth":
                session = tornado.escape.url_unescape(message['authentication'])
                if len(session.split('|')) == 2:
                    username = ((session.split('|')[0]).decode('hex').decode('utf-8')).strip()
                    hash = session.split('|')[1]
                    try:
                        if self.application.authentication.check_session(username, hash):
                            if self.application.db.get_server(self.server_id).Owner == username or self.application.authentication.is_user_admin(username):
                                self.auth = True
                            else:
                                self.write_message({"success": False, "message": "Required permissions not present."})
                        else:
                            self.write_message({"success": False, "message": "Bad authentication."})
                    except DoesNotExist:
                        self.write_message({'success': False, "message": "Bad authentication."})
                else:
                    self.write_message({'success': False, "message": "Bad authentication"})

                if self.auth:
                    self.filename = '/var/log/minecraft/%s%s.log' % (self.application.process_prefix, self.server_id)
                    self.mtime = os.path.getmtime(self.filename)
                    self.lines = message['lines']
                    self.callback = tornado.ioloop.PeriodicCallback(self.check_log, 250)
                    self.callback.start()

            elif message['action'] == "setLines":
                if self.auth:
                    self.lines = message['lines']
                else:
                    self.write_message({"success": False, "message": "Please authenticate first."})

            elif message['action'] == "getLog":
                if self.auth:
                    self.write_message({"success": True, "message": None, "log": (subprocess.check_output(['tail', '-n', str(self.lines), self.filename], shell=False))})
                else:
                    self.write_message({"success": False, "message": "Please authenticate first."})

            else:
                self.write_message({"success": False, "message": "Unrecognised action"})

        except ValueError or KeyError:
            self.write_message({"success": False, "message": "Not well formatted message."})

    def check_log(self):
        mtime = os.path.getmtime(self.filename)
        if mtime > self.mtime:
            self.mtime = mtime
            self.write_message({"success": True, "message": None, "log": (subprocess.check_output(['tail', '-n', str(self.lines), self.filename], shell=False))})

    def on_close(self):
        self.callback.stop()