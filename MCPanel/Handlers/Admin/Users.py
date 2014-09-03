__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAdminHandler
from tornado.web import authenticated
from Handlers.Base import admin


class AdminUsers(BaseAdminHandler):
    @asynchronous
    @authenticated
    @admin
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/users.template',
                    users=self.application.authentication.get_users())