__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServersHandler


class ServersIndexHandler(BaseServersHandler):
    @asynchronous
    @authenticated
    def get(self):
        #self.application.acl([], self.current_user, 1)
        self.render(self.application.settings['template_path'] + '/servers/index.template',
                    pageName="Minecraft Servers")
