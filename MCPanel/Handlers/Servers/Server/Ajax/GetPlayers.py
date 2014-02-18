__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerAjaxHandler
import tornado.iostream
from multiprocessing.pool import ThreadPool
import tornado.ioloop
from Minecraft.status import MinecraftQuery

_workers = ThreadPool(10)


class GetPlayersHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        server_id = str(server_id)
        if self.application.supervisor.is_process_running(self.application.process_prefix + server_id):
            self.server = self.application.db.get_server(server_id)
            run_background(run_query, self.on_complete, (self.server.Address, self.server.Port,))
        else:
            self.finish({"result": {"success": False, "message": "Server is not running", "max_players": None, "current_players": None, "players": []}})


    def on_complete(self, result):
        self.finish({"result": {"success": True, "message": None, "max_players": result['maxplayers'], "current_players": result['numplayers'], "players": result['players'], "version": result['version'], "software": result['software'], "plugins": result['plugins']}})


def run_background(func, callback, args=(), kwds={}):
    def _callback(result):
        tornado.ioloop.IOLoop.instance().add_callback(lambda: callback(result))
    _workers.apply_async(func, args, kwds, _callback)


def run_query(host, port):
    return MinecraftQuery(host, port, timeout=2).get_rules()