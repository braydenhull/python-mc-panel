__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Handlers.Servers.Ajax.Base import BaseServersAjaxHandler


class StopServerHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        if 'server_id' in self.request.arguments and 'force' in self.request.arguments:
            if self.application.supervisor.is_process_running(self.application.process_prefix + self.get_argument('server_id')):
                if self.get_argument('force') == "true":
                    self.finish({"result": {"message": None, "success": self.application.supervisor.stop_process(self.application.process_prefix + self.get_argument('server_id'))}})
                else:
                    self.finish({"result": {"message": None, "success": self.application.supervisor.run_command(self.application.process_prefix + self.get_argument('server_id'), "stop")}})
            else:
                self.finish({"result": {"message": "Process is not running", "success": False}})
        else:
            self.finish({"result": {"message": "Server ID or force is not specified.", "success": False}})