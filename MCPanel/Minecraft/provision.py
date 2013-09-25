__author__ = 'brayden'

import json
from urllib2 import HTTPError
import urllib2


class Bukkit:
    def __init__(self, channel="rb", build=0): # where 0 is latest
        # Channels are the build channels. valid ones as of now are: rb, beta, dev, next
        # more info at http://dl.bukkit.org/about/
        # Server flavours are: vanilla, bukkit, tekkit
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

    def get_download_url(self): # actual download will be handled in request handler for the purposes of async methods
        details = self._get_build_info()
        return {'URL': 'http://dl.bukkit.org' + details['file']['url'], 'MD5': details['file']['checksum_md5'], 'Size': details['file']['size'], 'Filename': details['target_filename'], 'Downloads': details['download_count'], 'Created': details['created']}
        # url, checksum, size