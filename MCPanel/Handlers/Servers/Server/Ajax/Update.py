__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServerAjaxHandler
import tornado.iostream
from multiprocessing.pool import ThreadPool
import tornado.ioloop
from Minecraft.provision import Bukkit
from Minecraft.provision import Vanilla

_workers = ThreadPool(10)


class UpdateServerHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'autostart' in self.request.arguments:
            autostart = True if self.get_argument('autostart') == 'true' else False
            self.server = self.application.db.get_server(server_id)
            if self.server.Type == "craftbukkit":
                run_background(run_bukkit_update, self.on_complete, (self.server.Stream, server_id, self, autostart,))
            elif self.server.Type == "vanilla":
                run_background(run_vanilla_update, self.on_complete, (self.server.Stream, server_id, self, autostart,))
        else:
            self.finish({"result": {"success": False, "message": "Autostart parameter not specified."}})

    def on_complete(self, result):
        self.finish({"result": {"success": result, "message": None}})


def run_background(func, callback, args=(), kwds={}):
    def _callback(result):
        tornado.ioloop.IOLoop.instance().add_callback(lambda: callback(result))
    _workers.apply_async(func, args, kwds, _callback)

def run_bukkit_update(stream, server_id, handler, autostart):
    return Bukkit(channel=stream, build=0).update(handler, server_id, stream, autostart)

def run_vanilla_update(stream, server_id, handler, autostart):
    return Vanilla(channel=stream, build=0).update(handler, server_id, stream, autostart)