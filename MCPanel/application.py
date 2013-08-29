__author__ = 'brayden'

import tornado.web
import tornado
import os


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', ),  # define a handler later when we actually have one!
        ]
        settings = dict(
            debug=False,
            gzip=True,
            login_url='/login',
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static')
        )
        tornado.web.Application.__init__(self, handlers, **settings)