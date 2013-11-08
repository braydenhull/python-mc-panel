__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerHandler
from tornado.web import HTTPError


class ServerIndexHandler(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        if self.application.db.serverExists(server_id):
            self.render(self.application.settings['template_path'] + '/servers/server/index.template', server_id=server_id)
        else:
            raise HTTPError(404)