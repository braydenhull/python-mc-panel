__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerHandler
from Minecraft.backup import Local


class ServerBackupHandler(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/backup.template', server_id=server_id, destinations=self.application.db.get_backup_destinations(), local_backup=Local)