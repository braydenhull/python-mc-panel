__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Handlers.Servers.Server.Base import BaseServerHandler
from Minecraft.status import ShortStatus


class ServerPlayersHandler(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/players.template', server_id=server_id, shortstatus=ShortStatus)