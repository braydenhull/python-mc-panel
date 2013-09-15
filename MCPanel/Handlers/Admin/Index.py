__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAdminHandler
from tornado.web import authenticated
from tornado import template


class AdminIndex(BaseAdminHandler):
    @asynchronous
    @authenticated
    def get(self):
        self.if_admin()
        # loader = template.Loader(self.application.settings['template_path'])
        # self.finish(
        #     loader.load("admin/index.template").generate(pageName="Admin Index", title="Minecraft Panel - Admin"))
        self.render(self.application.settings['template_path'] + '/admin/index.template', pageName="Admin Index")