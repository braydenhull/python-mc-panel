__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServerAjaxHandler


class SendCommandHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'command' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), self.get_argument('command'))}})
        else:
            self.finish({"result": {"success": False, "message": "Insufficient arguments"}})