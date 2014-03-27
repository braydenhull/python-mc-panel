__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler
from tornado.web import authenticated


class IndexHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        #self.render(self.application.settings['template_path'] + '/index.template')
        self.redirect(self.application.reverse_url('Servers_Index'))