__author__ = 'brayden'

import tornado.web
import base64
import tornado.escape
from peewee import DoesNotExist


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if 'session' in self.request.cookies:
            cookie = tornado.escape.url_unescape(self.get_cookie('session'))
            if len(cookie.split('|')) == 2:
                username = (base64.decodestring(cookie.split('|')[0])).strip()
                session = cookie.split('|')[1]
                try:
                    if self.application.checkSession(username, session):
                        return username
                except DoesNotExist:
                    return None
        return None

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update({
            'title': self.application.title,
            'name': self.application.name,
            'padding': 10,
        })

        return ns