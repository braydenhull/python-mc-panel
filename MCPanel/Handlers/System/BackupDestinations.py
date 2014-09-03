__author__ = 'brayden'

from Base import BaseSystemHandler
from tornado.web import asynchronous
from tornado.web import authenticated
from Minecraft.backup import Local


class SystemBackupDestinationsHandler(BaseSystemHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.render(self.application.settings['template_path'] + '/system/backup.template', backup_destinations=self.application.db.get_backup_destinations())

    def post(self):
        if self.get_argument('remote') == 'false':
            self.application.db.add_backup_destination(self.get_argument('friendly_name'), 'zip', self.get_argument('folder'), backup_limit=int(self.get_argument('backup_limit')))
            Local.add_destination(self.get_argument('folder'))
            self.render(self.application.settings['template_path'] + '/system/backup.template', backup_destinations=self.application.db.get_backup_destinations())
        else:
            self.finish('not implemented yet')