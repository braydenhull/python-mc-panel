__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAdminHandler
from tornado.web import authenticated
from tornado import template


class AdminRoles(BaseAdminHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.if_admin()
        loader = template.Loader(self.application.settings['template_path'])
        self.finish(loader.load("admin/roles.template").generate(pageName="Role Management",
                                                                 title="Minecraft Panel - Role Management",
                                                                 username=self.current_user))