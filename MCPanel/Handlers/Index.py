__author__ = 'brayden'

from tornado.web import asynchronous
from Handlers.Base import BaseHandler
from tornado.web import authenticated


class IndexHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        #self.application.acl([], self.current_user, 1)
        self.render(self.application.settings['template_path'] + '/index.template')