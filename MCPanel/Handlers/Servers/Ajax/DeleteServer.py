__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServersAjaxHandler
from peewee import DoesNotExist
from Minecraft.provision import Bukkit
import tornado.iostream
from multiprocessing.pool import ThreadPool
import tornado.ioloop

_workers = ThreadPool(10)


class DeleteServerHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        self.if_admin() # admin only function
        try:
            server = self.application.db.getServer(int(self.get_argument('server_id')))
            if server.Type == "craftbukkit":
                run_background(craftbukkit_delete, self.on_complete, (self.get_argument('server_id'), self.application,))
        except DoesNotExist:
            self.finish({'result': {'success': False, 'message': 'server_id does not exist'}})

    def on_complete(self, result):
        self.application.db.deleteServer(self.get_argument('server_id')) # cannot do this in the thread
        self.finish({"result": {"success": result, "message": None}})

def run_background(func, callback, args=(), kwds={}):
    def _callback(result):
        tornado.ioloop.IOLoop.instance().add_callback(lambda: callback(result))
    _workers.apply_async(func, args, kwds, _callback)

def craftbukkit_delete(server_id, application):
    return Bukkit().delete_server(server_id, application)