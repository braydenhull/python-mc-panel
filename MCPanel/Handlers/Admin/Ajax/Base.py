__author__ = 'brayden'

from MCPanel.Handlers.Admin.Base import BaseAdminHandler


class BaseAdminAjaxHandler(BaseAdminHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'text/json')
        if status_code == 403:
            self.finish({'result': {'success': False, 'message': 'Forbidden request.'}})
        else:
            self.finish({'result': {'success': False, 'message': status_code}})