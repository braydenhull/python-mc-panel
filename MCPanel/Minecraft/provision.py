__author__ = 'brayden'

import json
from urllib2 import HTTPError
import urllib2
from tornado.httpclient import AsyncHTTPClient
import os
import subprocess
import pwd


class Bukkit:
    def __init__(self, channel="rb", build=0):  # where 0 is latest
        # Channels are the build channels. valid ones as of now are: rb, beta, dev, next
        # more info at http://dl.bukkit.org/about/
        # Server flavours are: vanilla, bukkit, tekkit
        self.ws = None
        self.args = None
        self.channel = channel
        self.build = build
        self.user_agent = 'python-mc-panel/0.1-dev'
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [{'User-Agent', self.user_agent}]
        urllib2.install_opener(self.opener)

    class BukkitProvisionError(Exception):
        def __init__(self, message, name):
            self.message = message
            self.name = name

        def __str__(self):
            return repr(self.message)

    def _get_build_info(self):
        if not type(self.build) is int:
            raise self.BukkitProvisionError("Invalid build nubmer.", "InvalidBuildNumber")
        if self.build == 0:
            request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/view/latest/?_accept=application%2Fjson')
        else:
            try:
                request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/view/build-' + str(self.build) + '/?_accept=application%2Fjson')
            except HTTPError as e:
                if e.code == 404:
                    raise self.BukkitProvisionError("Build number not found.", "UnknownBuild")
                else:
                    raise self.BukkitProvisionError("Some HTTPError occurred: %s" % e, "UnknownHTTPError")
        result = json.loads(urllib2.urlopen(request).read())

        if result['is_broken']:
            raise self.BukkitProvisionError("Build is broken according to Bukkit", "BrokenBuild")

        return result

    def _get_builds(self, page=1):
        if not type(page) is int:
            raise TypeError
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/' +  self.channel + '/?_accept=application%2Fjson&page=' + str(page))
        result = urllib2.urlopen(request).read()
        result = json.loads(result)
        if result['results'] == 0:
            raise self.BukkitProvisionError("%s not recognised as a valid channel." % self.channel, "InvalidChannel Name")

        return result

    def get_download_url(self):  # actual download will be handled in request handler for the purposes of async methods
        details = self._get_build_info()
        return {'URL': 'http://dl.bukkit.org' + details['file']['url'], 'MD5': details['file']['checksum_md5'], 'Size': details['file']['size'], 'Filename': details['target_filename'], 'Downloads': details['download_count'], 'Created': details['created']}

    def install(self, ws, **kwargs):
        self.args = kwargs
        print kwargs
        client = AsyncHTTPClient()
        self.ws = ws
        self.channel = self.args['stream']
        self.build = 0 if self.args['build'] == "latest" else self.args['build']

        self.ws.write_message({"success": True, "message": "Grabbing Bukkit (this might take a while)"})
        client.fetch(self.get_download_url()['URL'], self._cb_download_handler, user_agent=self.user_agent, request_timeout=99999)  # if request_timeout isn't used, it'll die if it can't download fast enough

    def _cb_download_handler(self, response):
        if not response.error:
            self.ws.write_message({"message": "Completed download.", "success": True})
            home = self.ws.application.config.get('minecraft', 'home')
            if os.path.exists(home):
                os.system("useradd -m -s /bin/false -d %s/%s%s/ %s%s" % (home, self.ws.application.process_prefix, self.ws.server_id, self.ws.application.process_prefix, self.ws.server_id))
                self.ws.write_message({"success": True, "message": "Created new Linux user for server %s" % self.ws.server_id})
                home = pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_dir
                with open(home + '/minecraft.jar', 'wb') as f:
                    f.write(response.body)

                os.chown(home + '/minecraft.jar', pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_uid, pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_gid)
                os.chmod(home + '/minecraft.jar', 0700)

                self.ws.application.supervisor.write_program_config(self.ws.application.process_prefix + str(self.ws.server_id), os.path.dirname(self.ws.application.supervisor_config_path), self.args['memory'], self.ws.application.process_prefix + str(self.ws.server_id), home + '/minecraft.jar', additional_jar_options="--nojline --server-ip %s --server-port %s" % (self.args['address'], self.args['port']))
                self.ws.write_message({"success": True, "message": "Created supervisor config"})
                self.ws.write_message({"success": True, "message": "Starting server!"})
        else:
            self.ws.write_message({"success": False, "message": "HTTP Request was not successful. %s: %s" % (response.code, response.reason)})