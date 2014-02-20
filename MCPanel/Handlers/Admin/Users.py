__author__ = 'brayden'

from tornado.web import asynchronous
from Handlers.Admin.Base import BaseAdminHandler
from tornado.web import authenticated


class AdminUsers(BaseAdminHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.render(self.application.settings['template_path'] + '/admin/users.template',
                    users=self.application.db.get_users())