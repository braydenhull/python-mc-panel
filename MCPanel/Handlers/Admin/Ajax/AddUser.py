__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseAdminAjaxHandler


class AddUserHandler(BaseAdminAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        self.if_admin()
        if all(k in self.request.arguments for k in ("username", "password", "is_admin")):
            try:
                if self.get_argument('is_admin') == 'true':
                    is_admin = True
                else:
                    is_admin = False
                self.application.db.addUser(self.get_argument('username'), self.get_argument('password'),
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