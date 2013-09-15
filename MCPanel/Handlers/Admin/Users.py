__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAdminHandler
from tornado.web import authenticated
from tornado import template


class AdminUsers(BaseAdminHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.if_admin()
        # loader = template.Loader(self.application.settings['template_path'])
        # self.finish(
        #     loader.load("admin/users.template").generate(pageName="Admin Users", title="Minecraft Panel - Users",
        #                                                  users=self.application.db.getUsers()))
        self.render(self.application.settings['template_path'] + '/admin/users.template', pageName="Admin Users",
                    users=self.application.db.getUsers())