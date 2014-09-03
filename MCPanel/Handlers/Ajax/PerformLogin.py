__author__ = 'brayden'

from tornado.web import asynchronous
from . import BaseAjaxHandler
from peewee import DoesNotExist


class PerformLoginHandler(BaseAjaxHandler):
    @asynchronous
    def post(self):
        if all(k in self.request.arguments for k in ("username", "password", "expires")):
            if not self.get_argument('username') in self.application.usernames:
                self.finish({'result': {'success': False, 'message': 'Username/Password is incorrect.'}})
            else:
                try:
                    if self.application.authentication.check_credentials(self.get_argument('username'), self.get_argument('password')):
                        cookie_value =  (self.get_argument('username').encode('utf-8')).encode('hex') + '|' + self.application.authentication.make_session(
                            self.get_argument('username'))
                        self.set_cookie('session', cookie_value, expires_days=int(self.get_argument('expires')), path='/')
                        self.finish({'result': {'success': True, 'message': None,
                                                'cookie': cookie_value}})
                    else:
                        self.finish(
                            {'result':  {'success': False, 'message': 'Username/Password is incorrect.', 'cookie': None}})
                except DoesNotExist as e:
                    self.finish(
                        {'result': {'success': False, 'message': 'Username/Password is incorrect.', 'cookie': None}})
                # Technically means the row doesn't exist but don't want to hint the username exists
        else:
            self.finish({'result': {'success': False, 'message': 'Required arguments not present.', 'cookie': None}})