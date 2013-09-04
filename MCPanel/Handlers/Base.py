__author__ = 'brayden'

import tornado.web
import base64
import tornado.escape


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if 'session' in self.request.cookies:
            cookie = tornado.escape.url_unescape(self.get_cookie('session'))
            if len(cookie.split('|')) == 2:
                username = (base64.decodestring(cookie.split('|')[0])).strip()
                session = cookie.split('|')[1]
                if self.application.checkSession(username, session):
                    return username
        return None