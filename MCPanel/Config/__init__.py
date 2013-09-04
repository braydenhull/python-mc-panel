__author__ = 'brayden'

import os
import ConfigParser


class config:
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(os.path.join(os.path.expanduser('~'), '.mc_panel', 'config.cfg'))

    def get(self, section, option):  # mimics get behaviour
        return self.config.get(section, option)