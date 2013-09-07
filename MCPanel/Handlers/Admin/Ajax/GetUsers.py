__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseAdminAjaxHandler


class GetUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        self.if_admin()
        self.set_header('Content-Type', 'text/json')
        result = {"aaData": [], "results": [], "more": False}
        for user in self.application.db.getUsers():
            result['aaData'].append([user.ID, user.Username, user.Is_Admin])  # DataTable
            result['results'].append({'id': user.Username, 'text': user.Username})  # Select2
        self.finish(result)