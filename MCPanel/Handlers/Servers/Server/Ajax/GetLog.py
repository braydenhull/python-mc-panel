__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Handlers.Servers.Server.Ajax.Base import BaseServerAjaxHandler
import subprocess


class GetLogHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'lines' in self.request.arguments:
            self.finish({"result": {"success": True, "message": None, "log": (subprocess.check_output(['tail', '-n', self.get_argument('lines'), '/var/log/minecraft/%s%s.log' % (self.application.process_prefix, server_id)], shell=False)).decode()}})
        else:
            self.finish({"result": {"success": False, "message": "Insufficient arguments", "log": None}})