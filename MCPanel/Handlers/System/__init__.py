__author__ = 'brayden'

from .. import BaseHandler


class BaseSystemHandler(BaseHandler):
    def prepare(self):
        self.if_admin()