__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAdminHandler
from tornado.web import authenticated

class AdminRoles(BaseAdminHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/roles.template', pageName="Role Management")