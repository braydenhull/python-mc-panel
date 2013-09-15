__author__ = 'brayden'

from tornado.web import asynchronous
from MCPanel.Handlers.Base import BaseHandler
from tornado import template
from tornado.web import authenticated


class IndexHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        #self.application.acl([], self.current_user, 1)
        # loader = template.Loader(self.application.settings['template_path'])
        # self.finish(loader.load("index.template").generate(pageName="Minecraft Servers", title="Minecraft Panel - Servers"))
        self.render(self.application.settings['template_path'] + '/servers/index.template',
                    pageName="Minecraft Servers")
