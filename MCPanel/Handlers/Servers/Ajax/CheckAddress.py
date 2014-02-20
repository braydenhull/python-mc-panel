__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Handlers.Servers.Ajax.Base import BaseServersAjaxHandler


class CheckAddressHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        if 'port' in self.request.arguments and 'address' in self.request.arguments:
            if int(self.get_argument('port')) > 65535 or int(self.get_argument('port')) < 1:
                self.finish({'result': {'message': 'Server IP is out of usable range. (1-65535)', 'success': False, 'used': False}})
            elif not self.get_argument('port') == '' and self.application.db.is_address_taken(self.get_argument('address'), self.get_argument('port')):
                self.finish({'result': {'message': None, 'success': True, 'used': True}})
            else:
                self.finish({'result': {'message': None, 'success': True, 'used': False}})
        else:
            self.finish({'result': {'message': 'Port or address not specified', 'success': False, 'used': None}})