__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerAjaxHandler
from Minecraft.backup import Local


class DeleteBackupHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        destination = self.application.db.get_backup_destination_by_id(self.get_argument("destination_id"))
        if not destination.Remote:
            remove_file = True if self.get_argument('remove_file') == "true" else False
            Local(destination.ID, destination.Folder).remove_backup(self.application.process_prefix + server_id, self.get_argument('index'), remove_file=remove_file)
            self.finish({"result": {"message": None, "success": True}})
        else:
            self.finish({"result": {"message": "No valid destination available.", "success": False}})