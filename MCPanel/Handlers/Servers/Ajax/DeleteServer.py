__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServersAjaxHandler
from peewee import DoesNotExist
from Minecraft.provision import Bukkit


class DeleteServerHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        self.if_admin() # admin only function
        try:
            server = self.application.db.getServer(int(self.get_argument('server_id')))
            if server.Type == "craftbukkit":
                self.finish({'result': {'success': Bukkit().delete_server(self.get_argument('server_id'), self.application), 'message': None}})
        except DoesNotExist:
            self.finish({'result': {'success': False, 'message': 'server_id does not exist'}})