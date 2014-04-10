__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerHandler


class ServerSettingsHandler(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/settings.template', server_id=server_id)