__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServerHandler


class ServerPropertiesHandler(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        with open(self.application.config.get("minecraft", "home") + '/%s%s/server.properties' % (self.application.process_prefix, server_id)) as f:
            properties = f.read()
        self.render(self.application.settings['template_path'] + '/servers/server/properties.template', server_id=server_id, properties=properties)
    def post(self, server_id):
        with open(self.application.config.get("minecraft", "home") + '/%s%s/server.properties' % (self.application.process_prefix, server_id), 'w') as f:
            f.write(self.get_argument('properties'))
        self.render(self.application.settings['template_path'] + '/servers/server/properties.template', server_id=server_id, properties=self.get_argument('properties'))