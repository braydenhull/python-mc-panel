__author__ = 'brayden'

import os
import json
import time
import tarfile
import fnmatch
import zipfile


class Local:
    def __init__(self, destination_id, folder):
        self.destination_id = destination_id
        self.folder = folder
        self._backup_json = self._load_backup_json()

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
            #contents = {"backups": {"minecraft_1": [{"file": "/root/test/minecraft_1/2013-03-01/23-51.tar.gz", "date": 1393688673}]}}
            contents = {"backups": {}}
            with open(self.folder + '/backup.json', 'w') as f:
                json.dump(contents, f)
            return contents

    def get_all_backups(self):
        return self._backup_json['backups']

    def get_backups_by_server(self, server_name):
        if not server_name in self._backup_json['backups']:
            self.add_server(server_name)
        return self._backup_json['backups'][server_name]

    def get_backup(self, server_name, backup_index):
        return self._backup_json['backups'][server_name][backup_index]

    def _add_backup(self, server_name, file_path, date=None):
        current_json = self._backup_json
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

        self._backup_json = self._load_backup_json()

    def add_server(self, server_name):
        self._backup_json['backups'][server_name] = []
        with open(self.folder + '/backup.json', 'w') as f:
            json.dump(self._backup_json, f)

        self._backup_json = self._load_backup_json()

    def remove_backup(self, server_name, index, remove_file=True):
        current_json = self._load_backup_json()
        index = int(index)
        if not server_name in current_json['backups']:
            raise self.LocalBackupError("server_name given does not exist.")
        try:
            test = current_json['backups'][server_name][index]
        except IndexError:
            raise self.LocalBackupError("Backup index given does not exist.")
        if remove_file:
            os.remove(current_json['backups'][server_name][index]['file'])

        current_json['backups'][server_name].pop(index)
        with open(self.folder + '/backup.json', 'w') as f:
            json.dump(current_json, f)

        self._backup_json = self._load_backup_json()

    def backup_server_tar(self, server_name, server_folder, compression_mode='gz'): # backup server using tar format
        if not os.path.exists(self.folder + '/' + server_name + '/'):
            os.mkdir(self.folder + '/' + server_name + '/')

        time_now = int(time.time())

        file_path = self.folder + '/' + server_name + '/' + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(time_now))

        if compression_mode == 'gz':
            file_path += '.tar.gz'
            backup_file = tarfile.open(file_path, 'w|gz')
        elif compression_mode == 'bz2':
            file_path += '.tar.bz2'
            backup_file = tarfile.open(file_path, 'w|bz2')
        else:
            raise self.LocalBackupError("Compression mode given, %s, is not supported" % compression_mode)

        for root, directories, filenames in os.walk(server_folder):
            for filename in filenames:
                if not fnmatch.fnmatch(filename, '*.zip'):
                    backup_file.add(root + '/' + filename)

        self._add_backup(server_name, file_path, time_now)

        backup_file.close()

    def backup_server_zip(self, server_name, server_folder):
        if not os.path.exists(self.folder + '/' + server_name + '/'):
            os.mkdir(self.folder + '/' + server_name + '/')

        time_now = int(time.time())

        file_path = self.folder + '/' + server_name + '/' + time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(time_now)) + '.zip'

        with zipfile.ZipFile(file_path, 'w') as backup_zip:
            for root, directories, filenames in os.walk(server_folder):
                for filename in filenames:
                    if not fnmatch.fnmatch(filename, '*.zip'):
                        backup_zip.write(root + '/' + filename)

        self._add_backup(server_name, file_path, time_now)