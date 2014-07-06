__author__ = 'brayden'

import os


class Base(object):
    def __init__(self, directory): # directory of install, e.g. /home/minecraft_5/
        self.directory = directory

    def edit_port(self, new_port):
        properties = self._read_properties()
        properties['server-port'] = new_port
        properties['query.port'] = new_port
        self._write_properties(properties)

    def edit_address(self, new_address):
        properties = self._read_properties()
        properties['server-ip'] = new_address
        self._write_properties(properties)

    def _read_properties(self):
        properties = {}
        with open(os.path.join(self.directory, 'server.properties'), 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('#'): continue
                properties[line.split('=')[0]] = line.split('=')[1]
        return properties

    def _write_properties(self, content):
        if type(content) is not dict:
            raise TypeError('content parameter should be dict representing key-value pairs in Java properties files')

        with open(os.path.join(self.directory, 'server.properties'), 'w') as f:
            for key in content:
                f.write('%s=%s\r\n' % (key, content[key]))

class Vanilla(Base):
    pass

class Bukkit(Base):
    pass