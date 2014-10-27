__author__ = 'brayden'

import os
import ConfigParser
import Libs.log


class config:
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        sample = """[database]
type = sqlite
# if you're using something like SQLite, then host just needs to be the file, leave the rest blank
# supports sqlite, postgresql, mysql
#host = 127.0.0.1
host = /root/.mc_panel/db.sqlite
user = mcpanel
password = mcpanel
database = mcpanel
# seconds
ping-interval = 500

[panel]
# title is the prefix to all page titles, e.g. <your-title> - Home
# which would be in <title></title>
title = Minecraft
# The name is what will appear in the branding, HTML is allowed but recommended only for things like &mdash;
name = Python &mdash; Panel

[minecraft]
# Directory which contains all user home directories. Useful if there's a RAID array you wish to have servers on which is not mounted to /home
home = /home

[supervisor]
configuration = /etc/supervisor/supervisord.conf
"""
        self.defaults = {
            "database": {
                "type": "sqlite",
                "host": os.path.join(os.path.expanduser('~'), '.mc_panel', 'db.sqlite'),
                'user': None,
                'password': None,
                'database': None,
                'ping-interval': 500
            },
            "panel": {
                "title": "Minecraft",
                "name": "Python &mdash; Panel"
            },
            "minecraft": {
                "home": "/home"
            },
            "supervisor": {
                "configuration": "/etc/supervisor/supervisord.conf"
            }
        }
        self.config_file = os.path.join(os.path.expanduser('~'), '.mc_panel', 'config.cfg')
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            with open(self.config_file, 'w') as f:
                f.write(sample)
            self.config.read(self.config_file)

    def get(self, section, option):  # mimics get behaviour
        try:
            return self.config.get(section, option)
        except ConfigParser.NoSectionError or ConfigParser.NoOptionError as e:
            Libs.log.Log().warning("%s in %s is not present. Reverting to default." % (option, section))
            return self.defaults[section][option]