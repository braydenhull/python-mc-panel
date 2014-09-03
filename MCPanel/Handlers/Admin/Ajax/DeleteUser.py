__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseAdminAjaxHandler
from Handlers import admin


class DeleteUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    @admin
    def post(self):
        if 'user' in self.request.arguments:
            try:
                self.application.authentication.delete_user(self.get_argument('user'))
                self.application.generate_username_cache()
                self.finish({'result': {'success': True, 'message': 'User was successfully removed.'}})
            except Exception as e:
                self.finish({'result': {'success': False, 'message': e.message}})
        else:
            self.finish({'result': {'success': False, 'message': 'Required arguments not specified.'}})