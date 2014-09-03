__author__ = 'brayden'

from tornado.web import asynchronous
from . import BaseAdminAjaxHandler
from tornado.web import authenticated
from Handlers import admin


class EditUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    @admin
    def post(self):
        if all(k in self.request.arguments for k in ("username", "is_admin")):
            try:
                if self.get_argument("is_admin") == 'true':
                    is_admin = True
                else:
                    is_admin = False
                self.application.authentication.set_admin(self.get_argument('username'), is_admin=is_admin)
                self.application.generate_username_cache()
                self.finish({'result': {'success': True, 'message': 'User was successfully modified.'}})
            except Exception as e:
                self.finish({'result': {'success': False, 'message': e.message}})
        else:
            self.finish({'result': {'success': False, 'message': 'Required arguments not specified.'}})