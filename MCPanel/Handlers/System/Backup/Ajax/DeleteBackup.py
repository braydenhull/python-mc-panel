__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseBackupAjaxHandler
from Minecraft.backup import Local


class DeleteBackupHandler(BaseBackupAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, destination_id):
        destination = self.application.db.get_backup_destination_by_id(destination_id)
        if not destination.Remote:
            remove_file = True if self.get_argument('remove_file') == "true" else False
            Local(destination_id, destination.Folder).remove_backup(self.get_argument('server_name'), self.get_argument('index'), remove_file=remove_file)
            self.finish({"result": {"message": None, "success": True}})
        else:
            self.finish({"result": {"message": "No valid destination given.", "success": False}})