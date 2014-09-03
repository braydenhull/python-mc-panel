__author__ = 'brayden'

from .. import BaseServersHandler
from tornado.web import HTTPError


class BaseServerHandler(BaseServersHandler):
    def prepare(self):
        self.can_view_server(self.path_args[0])
        if not self.application.db.server_exists(self.path_args[0]):
            raise HTTPError(404)