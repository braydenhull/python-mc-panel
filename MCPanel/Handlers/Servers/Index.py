__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Handlers.Servers.Base import BaseServersHandler
from tornado.web import addslash


class ServersIndexHandler(BaseServersHandler):
    @asynchronous
    @authenticated
    @addslash
    def get(self):
        #self.application.acl([], self.current_user, 1)
        self.render(self.application.settings['template_path'] + '/servers/index.template')
