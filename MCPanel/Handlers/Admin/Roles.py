__author__ = 'brayden'

from tornado.web import asynchronous
from . import BaseAdminHandler
from tornado.web import authenticated
from Handlers import admin

class AdminRoles(BaseAdminHandler):
    @asynchronous
    @authenticated
    @admin
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/roles.template', pageName="Role Management")