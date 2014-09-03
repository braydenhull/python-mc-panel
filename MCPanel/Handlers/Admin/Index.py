__author__ = 'brayden'

from tornado.web import asynchronous
from . import BaseAdminHandler
from tornado.web import authenticated
from tornado.web import addslash
from Handlers import admin


class AdminIndex(BaseAdminHandler):
    @asynchronous
    @authenticated
    @addslash
    @admin
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/index.template')