__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseAjaxHandler
import base64
from peewee import DoesNotExist


class PerformLoginHandler(BaseAjaxHandler):
    @asynchronous
    def post(self):
        self.set_header('Content-Type', 'text/json')
        if all(k in self.request.arguments for k in ("username", "password", "expires")):
            try:
                if self.application.db.checkCredentials(self.get_argument('username'), self.get_argument('password')):
                    cookie_value = base64.encodestring(
                        self.get_argument('username')).strip() + '|' + self.application.makeSession(
                        self.get_argument('username'))
                    self.set_cookie('session', cookie_value, expires_days=int(self.get_argument('expires')), path='/')
                    self.finish({'result': {'success': True, 'message': None,
                                            'cookie': cookie_value}})
                else:
                    self.finish(
                        {'result': {'success': False, 'message': 'Username/Password is incorrect.', 'cookie': None}})
            except DoesNotExist as e:
                self.finish(
                    {'result': {'success': False, 'message': 'Username/Password is incorrect.', 'cookie': None}})
                # Technically means the row doesn't exist but don't want to hint the username exists
        else:
            self.finish({'result': {'success': False, 'message': 'Required arguments not present.', 'cookie': None}})