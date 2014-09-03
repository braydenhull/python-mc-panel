__author__ = 'brayden'

from .. import BaseSystemHandler
from tornado.web import HTTPError


class BaseBackupHandler(BaseSystemHandler):
    def prepare(self):
        self.if_admin()
        if not self.application.db.backup_destination_exists(self.path_args[0]):
            raise HTTPError(404)