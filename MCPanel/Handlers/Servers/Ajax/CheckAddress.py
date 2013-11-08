__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServersAjaxHandler


class CheckAddressHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        if 'port' in self.request.arguments and 'address' in self.request.arguments:
            if not self.get_argument('port') == '' and self.application.db.isAddressTaken(self.get_argument('address'), self.get_argument('port')):
                self.finish({'result': {'message': None, 'success': True, 'used': True}})
            else:
                self.finish({'result': {'message': None, 'success': True, 'used': False}})
        else:
            self.finish({'result': {'message': 'Port or address not specified', 'success': False, 'used': None}})