__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from tornado.web import MissingArgumentError
from Base import BaseServersAjaxHandler
from Minecraft.provision import Bukkit


class GetInfoHandler(BaseServersAjaxHandler):
    @asynchronous
    @authenticated
    def post(self):
        try:
            if not 'server_type' in self.request.arguments:
                self.finish({"result": {"success": False, "message": "server_type not defined", "results": None}})
            else:
                if self.get_argument('server_type') == 'craftbukkit':
                    try:
                        if self.get_argument('request_type') == 'get_builds':
                            self.finish({"result": {"success": True, "message": None, "results": Bukkit(channel=self.get_argument('stream')).get_builds()}})
                        elif self.get_argument('request_type') == 'get_streams':
                            self.finish({"result": {"success": True, "message": None, "results": Bukkit().get_streams()}})
                        elif self.get_argument('request_type') == 'get_build_info':
                            self.finish({"result": {"success": True, "message": None, "results": Bukkit(build=int(self.get_argument('build'))).get_build_info()}})
                    except Bukkit.BukkitProvisionError as e:
                        self.finish({"result": {"success": False, "message": "%s: %s" % (e.message, e.name), "results": None}})
                else:
                    self.finish({"result": {"success": False, "message": "server_type not implemented.", "results": None}})
        except MissingArgumentError as e:
            self.finish({"result": {"success": False, "message": "MissingArgumentError: %s" % e, "results": None}})