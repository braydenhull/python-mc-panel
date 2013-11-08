__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAdminHandler
from tornado.web import authenticated
from tornado.web import addslash


class AdminIndex(BaseAdminHandler):
    @asynchronous
    @authenticated
    @addslash
    def get(self):
        self.if_admin()
        self.render(self.application.settings['template_path'] + '/admin/index.template')