__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServerAjaxHandler


class KickPlayerHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'player' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), "kick " + self.get_argument('player'))}})
        else:
            self.finish({"result": {"success": False, "message": "Player not defined."}})