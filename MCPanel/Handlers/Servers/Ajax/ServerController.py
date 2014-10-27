__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServersAjaxHandler
from peewee import DoesNotExist
from Minecraft.provision import Bukkit
import tornado.iostream
from multiprocessing.pool import ThreadPool
import tornado.ioloop
from Handlers import admin


class StartServer(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        if 'server_id' in self.request.arguments:
            if not self.application.supervisor.is_process_running(self.application.process_prefix + self.get_argument('server_id')):
                self.finish({"result": {"message": None, "success": self.application.supervisor.start_process(self.application.process_prefix + self.get_argument('server_id'))}})
            else:
                self.finish({"result": {"message": "Process is already running", "success": False}})
        else:
            self.finish({"result": {"message": "Server ID is not specified.:", "success": False}})


class StopServer(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        if 'server_id' in self.request.arguments and 'force' in self.request.arguments:
            self.can_view_server(self.get_argument('server_id'))
            if self.application.supervisor.is_process_running(self.application.process_prefix + self.get_argument('server_id')):
                if self.get_argument('force') == "true":
                    self.finish({"result": {"message": None, "success": self.application.supervisor.stop_process(self.application.process_prefix + self.get_argument('server_id'))}})
                else:
                    self.finish({"result": {"message": None, "success": self.application.supervisor.run_command(self.application.process_prefix + self.get_argument('server_id'), "stop")}})
            else:
                self.finish({"result": {"message": "Process is not running", "success": False}})
        else:
            self.finish({"result": {"message": "Server ID or force is not specified.", "success": False}})


_workers = ThreadPool(10)

class DeleteServer(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    @admin
    def post(self):
        try:
            server = self.application.db.get_server(int(self.get_argument('server_id')))
            if server.Type == "craftbukkit" or server.Type == "vanilla":
                run_background(craftbukkit_delete, self.on_complete, (self.get_argument('server_id'), self.application,))
        except DoesNotExist:
            self.finish({'result': {'success': False, 'message': 'server_id does not exist'}})

    def on_complete(self, result):
        self.application.db.delete_server(self.get_argument('server_id')) # cannot do this in the thread
        self.finish({"result": {"success": result, "message": None}})

def run_background(func, callback, args=(), kwds={}):
    def _callback(result):
        tornado.ioloop.IOLoop.instance().add_callback(lambda: callback(result))
    _workers.apply_async(func, args, kwds, _callback)

def craftbukkit_delete(server_id, application):
    return Bukkit.delete_server(server_id, application)