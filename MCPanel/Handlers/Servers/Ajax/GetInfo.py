__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from tornado.web import MissingArgumentError
from Base import BaseServersAjaxHandler
from Minecraft.provision import Bukkit
from Minecraft.provision import Vanilla


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
                            Bukkit(channel=self.get_argument('stream')).get_builds(self)
                        elif self.get_argument('request_type') == 'get_streams':
                            Bukkit().get_streams(self)
                        elif self.get_argument('request_type') == 'get_build_info':
                            Bukkit(build=int(self.get_argument('build'))).get_build_info(self)
                    except Bukkit.BukkitProvisionError as e:
                        self.finish({"result": {"success": False, "message": "%s: %s" % (e.message, e.name), "results": None}})
                elif self.get_argument('server_type') == 'vanilla':
                    try:
                        if self.get_argument('request_type') == 'get_builds':
                            Vanilla(channel=self.get_argument('stream')).get_builds(self)
                        elif self.get_argument('request_type') == 'get_streams':
                            Vanilla.get_streams(self)
                        elif self.get_argument('request_type') == 'get_build_info':
                            Vanilla(build=self.get_argument('build')).get_build_info(self)
                    except Vanilla.VanillaProvisionError as e:
                        self.finish({"result": {"success": False, "message": "%s: %s" % (e.message, e.name), "results": None}})
                else:
                    self.finish({"result": {"success": False, "message": "server_type not implemented.", "results": None}})
        except MissingArgumentError as e:
            self.finish({"result": {"success": False, "message": "MissingArgumentError: %s" % e, "results": None}})