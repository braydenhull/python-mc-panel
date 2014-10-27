__author__ = 'brayden'

from tornado.websocket import WebSocketHandler


class BaseWebSocketHandler(WebSocketHandler):
    def initialize(self, **kwargs):
        self.page_title = kwargs['title']