__author__ = 'brayden'

import sqlalchemy
import ConfigParser
import os


class Database():
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(os.path.join(os.path.expanduser('~'), '.mc_panel', 'config.cfg'))
        # maybe add some stuff too