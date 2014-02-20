__author__ = 'brayden'

from ..Base import BaseHandler


class BaseAdminHandler(BaseHandler):
    def prepare(self):
        self.if_admin()