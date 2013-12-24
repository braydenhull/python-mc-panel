__author__ = 'brayden'

from ..Base import BaseServersHandler


class BaseServersAjaxHandler(BaseServersHandler):
    def write_error(self, status_code, **kwargs):
        if status_code == 403:
            self.finish({'result': {'success': False, 'message': 'Forbidden request.'}})
        else:
            self.finish({'result': {'success': False, 'message': status_code}})