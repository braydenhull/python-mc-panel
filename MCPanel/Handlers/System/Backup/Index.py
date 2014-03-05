__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseBackupHandler
from Minecraft.backup import Local


class BackupIndexHandler(BaseBackupHandler):
    @asynchronous
    @authenticated
    def get(self, destination_id):
        destination = self.application.db.get_backup_destination_by_id(destination_id)
        if destination.Remote:
            self.render(self.application.settings['template_path'] + '/system/backup/remote.template', destination_id=destination_id, destination=destination)
        else:
            self.render(self.application.settings['template_path'] + '/system/backup/local.template', destination_id=destination_id, destination=destination, backups=Local(destination_id, destination.Folder).get_all_backups())