__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Handlers.Servers.Ajax.Base import BaseServersAjaxHandler


class StartServerHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        if 'server_id' in self.request.arguments:
            if not self.application.supervisor.is_process_running(self.application.process_prefix + self.get_argument('server_id')):
                self.finish({"result": {"message": None, "success": self.application.supervisor.start_process(self.application.process_prefix + self.get_argument('server_id'))}})
            else:
                self.finish({"result": {"message": "Process is already running", "success": False}})
        else:
            self.finish({"result": {"message": "Server ID is not specified.:", "success": False}})