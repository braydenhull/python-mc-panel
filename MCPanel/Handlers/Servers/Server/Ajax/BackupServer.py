__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from tornado.ioloop import IOLoop
from Base import BaseServerAjaxHandler
from Minecraft.backup import Local
from functools import partial
from datetime import timedelta


class BackupServerHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        destination = self.application.db.get_backup_destination_by_id(self.get_argument('destination_id'))
        if not destination.Remote:
            backup = Local(destination.ID, destination.Folder)
            server_name = self.application.process_prefix + server_id
            server_folder = self.application.config.get('minecraft', 'home') + '/%s%s/' % (self.application.process_prefix, server_id)
            if destination.Backup_Limit == 0 or self.application.usernames[self.current_user]['Is_Admin'] or not len(backup.get_backups_by_server(server_name)) >= destination.Backup_Limit:
                self.application.supervisor.run_command(server_name, 'save-off')
                IOLoop.instance().add_timeout(timedelta(seconds=2), partial(self.callback, backup, server_name, server_folder))
            else:
                self.finish({"result": {"message": "Reached backup limit.", "success": False}})
        else:
            self.finish({"result": {"message": "Invalid destination argument given.", "success": False}})

    def callback(self, backup, server_name, server_folder):
        if self.get_argument('backup_type') == 'tar':
            backup.backup_server_tar(server_name, server_folder)
            self.application.supervisor.run_command(server_name, 'save-on')
            self.finish({"result": {"message": None, "success": True}})
        elif self.get_argument('backup_type') == 'zip':
            backup.backup_server_zip(server_name, server_folder)
            self.application.supervisor.run_command(server_name, 'save-on')
            self.finish({"result": {"message": None, "success": True}})
        else:
            self.finish({"result": {"message": "Invalid backup_type given.", "success": False}})