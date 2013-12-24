__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerAjaxHandler
from tornado.web import HTTPError
import subprocess
from tornado.web import escape


class GetLogHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'lines' in self.request.arguments:
            self.finish({"result": {"success": True, "message": None, "log": (subprocess.check_output(['tail', '-n', self.get_argument('lines'), '/var/log/minecraft/minecraft_%s.log' % server_id], shell=False))}})
        else:
            self.finish({"result": {"success": False, "message": "Insufficient arguments", "log": None}})