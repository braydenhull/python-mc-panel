__author__ = 'brayden'

from ..Base import BaseHandler


class BaseSystemHandler(BaseHandler):
    def prepare(self):
        self.if_admin()