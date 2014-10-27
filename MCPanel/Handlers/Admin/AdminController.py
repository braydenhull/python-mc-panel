__author__ = 'brayden'

from tornado.web import asynchronous
from . import BaseAdminHandler
from tornado.web import authenticated
from tornado.web import addslash
from Handlers import admin


class Index(BaseAdminHandler):
    @asynchronous
    @authenticated
    @addslash
    @admin
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/index.template')


class Roles(BaseAdminHandler):
    @asynchronous
    @authenticated
    @admin
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/roles.template')


class Users(BaseAdminHandler):
    @asynchronous
    @authenticated
    @admin
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/users.template',
                    users=self.application.authentication.get_users())