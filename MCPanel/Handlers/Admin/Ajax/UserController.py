__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseAdminAjaxHandler
from Handlers import admin


class GetUser(BaseAdminAjaxHandler):
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


class EditUser(BaseAdminAjaxHandler):
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


class DeleteUser(BaseAdminAjaxHandler):
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


class AddUser(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    @admin
    def post(self):
        if all(k in self.request.arguments for k in ("username", "password", "is_admin")):
            try:
                if self.get_argument('is_admin') == 'true':
                    is_admin = True
                else:
                    is_admin = False
                self.application.authentication.add_user(self.get_argument('username'), self.get_argument('password'),
                                            is_admin=is_admin)
                self.application.generate_username_cache()
                self.finish({'result': {'success': True, 'message': 'User was successfully created.'}})
            except Exception as e:
                if e[0] == 1062:
                # special MySQL code for integrity error which occurs on duplicate entries.
                # who knows what happens when using sqlite/postgresql
                    self.finish({'result': {'success': False, 'message': 'Integrity error!\r\nUser already exists.'}})
                else:
                    self.finish({'result': {'success': False, 'message': str(e)}})
        else:
            self.finish({'result': {'success': False, 'message': 'Required arguments not specified.'}})