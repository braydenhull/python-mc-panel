__author__ = 'brayden'

from Base import BaseSystemHandler
from tornado.web import asynchronous
from tornado.web import authenticated


class SystemBackupDestinationsHandler(BaseSystemHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.render(self.application.settings['template_path'] + '/system/backup.template', backup_destinations=self.application.db.get_backup_destinations())