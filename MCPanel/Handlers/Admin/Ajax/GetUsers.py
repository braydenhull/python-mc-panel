__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseAdminAjaxHandler


class GetUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        result = {"result": {'users': []}}
        for user in self.application.db.getUsers():
            result['result']['users'].append({'username': user.Username, 'is_admin': user.Is_Admin})
        result['result']['success'] = True
        result['result']['message'] = None
        self.finish(result)