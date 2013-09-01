__author__ = 'brayden'

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return 'Test'