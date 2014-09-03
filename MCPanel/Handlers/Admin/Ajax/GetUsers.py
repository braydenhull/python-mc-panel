__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseAdminAjaxHandler
from Handlers import admin


class GetUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    @admin
    def post(self):
        result = {"result": {'users': []}}
        for user in self.application.authentication.get_users():
            result['result']['users'].append({'username': user.Username, 'is_admin': user.Is_Admin})
        result['result']['success'] = True
        result['result']['message'] = None
        self.finish(result)