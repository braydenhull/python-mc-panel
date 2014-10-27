__author__ = 'brayden'

from tornado.websocket import WebSocketHandler


class BaseServerWebSocketHandler(WebSocketHandler):
    def initialize(self, **kwargs):
        self.page_title = kwargs['title']