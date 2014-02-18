__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from tornado.web import addslash
from Base import BaseUserHandler


class UserIndexHandler(BaseUserHandler):
    @asynchronous
    @authenticated
    @addslash
    def get(self):
        self.render(self.application.settings['template_path'] + '/user/index.template', message='')

    def post(self):
        if self.get_argument('method') == 'changePassword':
            self.application.db.change_password(self.current_user, new_password=self.get_argument('new_password'))
            self.render(self.application.settings['template_path'] + '/user/index.template', message='Successfully changed password')
        else:
            self.render(self.application.settings['template_path'] + '/user/index.template', message='Specified method does not match any known method.')