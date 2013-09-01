__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler
from tornado import template
from tornado.web import authenticated


class IndexHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        loader = template.Loader(self.application.settings['template_path'])
        self.finish(loader.load("index.template").generate(pageName="Index", title="Minecraft Panel - Home",
                                                           username=self.current_user))