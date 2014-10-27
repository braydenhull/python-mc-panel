__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from . import BaseServerAjaxHandler
import tornado.iostream
from multiprocessing.pool import ThreadPool
import tornado.ioloop
from Minecraft.status import MinecraftQuery
import json
import os


class UnbanPlayer(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'player' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), 'pardon ' + self.get_argument('player'))}})
        else:
            self.finish({"result": {"success": False, "message": "Player argument missing"}})


class OpPlayer(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'player' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), 'op ' + self.get_argument('player'))}})
        else:
            self.finish({"result": {"success": False, "Message": "Player argument missing"}})


class KickPlayer(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'player' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), "kick " + self.get_argument('player'))}})
        else:
            self.finish({"result": {"success": False, "message": "Player not defined."}})


_workers = ThreadPool(10)


class GetPlayers(BaseServerAjaxHandler):
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


class GetOperators(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        ops = []

        if os.path.exists('%s/%s%s/ops.json' % (self.application.config.get('minecraft', 'home'), self.application.process_prefix, server_id)):
            with open('%s/%s%s/ops.json' % (self.application.config.get('minecraft', 'home'), self.application.process_prefix, server_id), 'r') as f:
                data = json.load(f)
            for op in data:
                ops.append(op['name'])
        else:
            with open('%s/%s%s/ops.txt' % (self.application.config.get('minecraft', 'home'), self.application.process_prefix, server_id)) as f:
                for line in f.readlines():
                    if line.startswith('#'): continue

                    ops.append(line.strip())

        self.finish({"result": {"success": True, "message": None, "ops": ops}})


class GetBannedPlayers(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if os.path.exists(self.application.config.get('minecraft', 'home') + '/%s%s/banned-players.json' % (self.application.process_prefix, server_id)):
            with open(self.application.config.get('minecraft', 'home') + '/%s%s/banned-players.json' % (self.application.process_prefix, server_id), 'r') as f:
                data = json.load(f)

            result = {"players": [], "details": {}}

            for player in data:
                result['players'].append(player['name'])
                result['details'][player['name']] = {"Ban Date": player['created'], "Banned By": player['source'], "Banned Until": player['expires'], "Reason": player['reason']}
        else:
            with open(self.application.config.get('minecraft', 'home') + '/%s%s/banned-players.txt' % (self.application.process_prefix, server_id), 'r') as f:
                lines = list(line for line in (l.strip() for l in f) if line) # this mess provided by http://stackoverflow.com/a/4842095/2077881

            result = {"players": [], "details": {}}

            for line in lines:
                if line.startswith('#'):
                    continue

                player = line.split('|')
                result['players'].append(player[0])

                if len(player) > 1:  # back in my day banned-players.txt was just a list of names
                    result['details'][player[0]] = {
                        "Ban Date": player[1],
                        "Banned By": player[2],
                        "Banned Until": player[3],
                        "Reason": player[4]
                    }
                else:
                    result['details'][player[0]] = {
                        "Ban Date": "Not Available",
                        "Banned By": "Unknown",
                        "Banned Until": "Forever",
                        "Reason": "Unknown"
                    }

        self.finish({"result": {"success": True, "message": None, "results": result}})


class DeopPlayer(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'player' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), "deop " + self.get_argument('player'))}})
        else:
            self.finish({"result": {"success": False, "message": "Player not defined."}})


class BanPlayer(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        if 'player' in self.request.arguments:
            self.finish({"result": {"message": None, "success": self.application.supervisor.run_command('%s%s' % (self.application.process_prefix, server_id), "ban " + self.get_argument('player'))}})
        else:
            self.finish({"result": {"success": False, "message": "Player not defined."}})