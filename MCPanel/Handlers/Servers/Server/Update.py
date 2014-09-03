__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServerHandler


class ServerUpdateHandler(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/update.template', server_id=server_id)