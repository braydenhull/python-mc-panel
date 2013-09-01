__author__ = 'brayden'

import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.web
import tornado
import os
from application import Application
os.chdir(os.path.dirname(__file__))  # fixes some quirk with chdir on supervisor, though not sure if needed
# last time I tried without, it worked fine


def main():
    tornado.options.options.parse_command_line()
    application = Application()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port=6060, address=None)  # ipv4 and v6
    tornado.ioloop.IOLoop.instance().start()

main()