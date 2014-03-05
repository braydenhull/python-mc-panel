__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerAjaxHandler
import psutil
from multiprocessing.pool import ThreadPool
import tornado.ioloop
import tornado.iostream
import time

_workers = ThreadPool(20)


class GetProcessInfoHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        pid = self.application.supervisor.get_pid(self.application.process_prefix + server_id)
        try:
            process = psutil.Process(pid)
            self.process = process
            self.server_id = server_id
            self.finish({"result": {
            "success": True,
            "message": None,
            "data": {
                "cpu_percent": round(psutil.cpu_percent(interval=0)),
                "process_create_time": round(self.process.create_time, 0),
                "current_time": round(time.time(), 0),
                "current_memory_percent": round(self.process.get_memory_percent(), 0),
                "memory_allocation_percent": round(100 * (self.application.db.get_server(self.server_id).Memory * 1024) / (psutil.virtual_memory().total / 1024), 0),
                "current_memory_as_percentage_of_allocation": round(100 * (self.process.get_memory_info().rss / 1024 / 1024) / self.application.db.get_server(self.server_id).Memory, 0)

            }
        }})
        except psutil.NoSuchProcess as e:
            self.finish({"result": {"success": False, "message": "Server is not running or could not find valid PID."}})