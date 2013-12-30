__author__ = 'brayden'

import tornado.web
import base64
import tornado.escape
from peewee import DoesNotExist
from tornado.web import HTTPError


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if 'session' in self.request.cookies:
            cookie = tornado.escape.url_unescape(self.get_cookie('session'))
            if len(cookie.split('|')) == 2:
                username = (((cookie.split('|')[0])).decode('hex').decode('utf-8')).strip()
                session = cookie.split('|')[1]
                try:
                    if self.application.check_session(username, session):
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
            'servers': self.application.db.getServers(),
        })
        return ns

    def if_admin(self):
        try:
            if not self.application.db.isUserAdmin(self.current_user):
                raise HTTPError(403)
        except DoesNotExist as e:
            raise HTTPError(403)

    def can_view_server(self, server_id):
        try:
            if not self.application.db.isUserAdmin(self.current_user):
                if not self.application.db.getServer(server_id).Owner == self.current_user:
                    raise HTTPError(403)
        except DoesNotExist:
            raise HTTPError(403)