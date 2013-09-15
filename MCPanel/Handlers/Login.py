__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler
from tornado import template


class LoginHandler(BaseHandler):
    @asynchronous
    def get(self):
        # loader = template.Loader(self.application.settings['template_path'])
        # self.finish(
        #     loader.load("login.template").generate(pageName="Login", title="Minecraft Panel - Login",
        #                                            current_user="Not Logged In"))
        self.render(self.application.settings['template_path'] + '/login.template', pageName="Login",
                    current_user="Not Logged In")