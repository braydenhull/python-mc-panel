__author__ = 'brayden'

import tornado.web
import tornado.escape
from peewee import DoesNotExist
from tornado.web import HTTPError
import functools


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if 'session' in self.request.cookies:
            cookie = tornado.escape.url_unescape(self.get_cookie('session'))
            if len(cookie.split('|')) == 2:
                username = (((cookie.split('|')[0])).decode('hex').decode('utf-8')).strip()
                session = cookie.split('|')[1]
                try:
                    if self.application.authentication.check_session(username, session):
                        return username
                except DoesNotExist:
                    return None
        return None

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update({
            'title': self.application.title,
            'name': self.application.name,
            'process_prefix': self.application.process_prefix,
            'servers': self.application.db.get_servers(),
        })
        return ns

    def if_admin(self):
        try:
            if self.current_user is None:
                self.redirect(self.application.settings['login_url'])
            elif not self.application.authentication.is_user_admin(self.current_user):
                raise HTTPError(403)
        except DoesNotExist as e:
            raise HTTPError(403)

    def can_view_server(self, server_id):
        if self.current_user in self.application.usernames:
            try:
                if not self.application.authentication.is_user_admin(self.current_user):
                    if not self.application.authentication.get_server(server_id).Owner == self.current_user:
                        raise HTTPError(403)
            except DoesNotExist:
                raise HTTPError(403)

def admin(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            if self.current_user is None:
                self.redirect(self.application.settings['login_url'])
            elif not self.application.authentication.is_user_admin(self.current_user):
                raise HTTPError(403)
        except DoesNotExist:
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper