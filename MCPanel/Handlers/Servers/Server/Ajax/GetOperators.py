__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerAjaxHandler


class GetOperatorsHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        ops = []

        with open('%s/%s%s/ops.txt' % (self.application.config.get('minecraft', 'home'), self.application.process_prefix, server_id)) as f:
            for line in f.readlines():
                if line.startswith('#'): continue

                ops.append(line.strip())

        self.finish({"result": {"success": True, "message": None, "ops": ops}})