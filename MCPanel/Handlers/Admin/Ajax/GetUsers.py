__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseAdminAjaxHandler


class GetUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        self.if_admin()
        result = {"result": []}
        for user in self.application.db.getUsers():
            result['result'].append({'id': user.ID, 'username': user.Username, 'is_admin': user.Is_Admin})  # Select2
        self.finish(result)