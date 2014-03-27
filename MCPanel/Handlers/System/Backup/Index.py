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
            backup = Local(destination_id, destination.Folder)
            self.render(self.application.settings['template_path'] + '/system/backup/local.template', destination_id=destination_id, destination=destination, backups=backup.get_all_backups())

    def post(self, destination_id):
        destination = self.application.db.get_backup_destination_by_id(destination_id)
        if not destination.Remote:
            self.application.db.set_local_backup_settings(destination_id, self.get_argument('friendly_name'), self.get_argument('folder'), self.get_argument('backup_limit'))
            destination = self.application.db.get_backup_destination_by_id(destination_id)
            backup = Local(destination_id, destination.Folder)
            self.render(self.application.settings['template_path'] + '/system/backup/local.template', destination_id=destination_id, destination=destination, backups=backup.get_all_backups())