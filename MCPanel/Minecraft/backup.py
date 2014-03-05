__author__ = 'brayden'

import os
import json
import time


class Local:
    def __init__(self, destination_id, folder):
        self.destination_id = destination_id
        self.folder = folder

    class LocalBackupError(Exception):
        def __init__(self, message, name="LocalBackupError"):
            self.message = message
            self.name = name

        def __str__(self):
            return repr("%s: %s" % (self.name, self.message))

    def _load_backup_json(self):
        if os.path.exists(self.folder + '/backup.json'):
            with open(self.folder + '/backup.json', 'r') as f:
                return json.load(f)
        else:
            contents = {"backups": {"minecraft_1": [{"file": "/root/test/minecraft_1/2013-03-01/23-51.tar.gz", "date": 1393688673}]}}
            with open(self.folder + '/backup.json', 'w') as f:
                json.dump(contents, f)
            return contents

    def get_all_backups(self):
        return self._load_backup_json()['backups']

    def get_backups_by_server(self, server_name):
        return self._load_backup_json()['backups'][server_name]

    def get_backup(self, server_name, backup_index):
        return self._load_backup_json()['backups'][server_name][backup_index]

    def add_backup(self, server_name, file_path, date=None):
        current_json = self._load_backup_json()
        if not server_name in current_json['backups']:
            current_json['backups'][server_name] = []

        if type(date) is None:
            date = int(time.time())

        try:
            time.gmtime(date)
        except ValueError:
            raise self.LocalBackupError("Date given should be 'time since epoch'.", "InvalidDate")

        current_json['backups'][server_name].append({"file": file_path, "date": date})

        with open(self.folder + '/backup.json', 'w') as f:
            json.dump(current_json, f)