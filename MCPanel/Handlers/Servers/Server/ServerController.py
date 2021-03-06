__author__ = 'brayden'

from tornado.web import asynchronous, os
from tornado.web import authenticated
from . import BaseServerHandler
from Minecraft.backup import Local
from Minecraft.status import ShortStatus
import netifaces
import tornado.ioloop
from Minecraft.helpers import Vanilla, Bukkit, Base


class Backup(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/backup.template', server_id=server_id, destinations=self.application.db.get_backup_destinations(), local_backup=Local)


class Console(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/console.template', server_id=server_id)


class Index(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/index.template', server_id=server_id)


class Players(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/players.template', server_id=server_id, shortstatus=ShortStatus)


class Plugin(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/plugins.template', server_id=server_id)


class Properties(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        with open(self.application.config.get("minecraft", "home") + '/%s%s/server.properties' % (self.application.process_prefix, server_id)) as f:
            properties = f.read()
        self.render(self.application.settings['template_path'] + '/servers/server/properties.template', server_id=server_id, properties=properties)

    @asynchronous
    @authenticated
    def post(self, server_id):
        with open(self.application.config.get("minecraft", "home") + '/%s%s/server.properties' % (self.application.process_prefix, server_id), 'w') as f:
            f.write(self.get_argument('properties'))
        self.render(self.application.settings['template_path'] + '/servers/server/properties.template', server_id=server_id, properties=self.get_argument('properties'))


class Settings(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        interfaces = []
        for interface in netifaces.interfaces(): interfaces.append(netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])
        self.render(self.application.settings['template_path'] + '/servers/server/settings.template', server_id=server_id, message='', error=False, interfaces=interfaces)

    @asynchronous
    @authenticated
    def post(self, server_id):
        self.server_id = server_id
        interfaces = []
        for interface in netifaces.interfaces(): interfaces.append(netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])
        server = self.application.db.get_server(server_id)
        change_requiring_restart = False # make true if the minecraft instance needs a reboot due to a change, e.g.: memory change
        error = False
        message = ''
        if self.get_argument('address') != server.Address or int(self.get_argument('port')) != server.Port:
            if not self.application.db.is_address_taken(self.get_argument('address'), self.get_argument('port'), no_match_all=True):
                if server.Type == "vanilla":
                    Vanilla(os.path.join(self.application.config.get('minecraft', 'home'), self.application.process_prefix + server_id)).edit_port(int(self.get_argument('port')))
                    Vanilla(os.path.join(self.application.config.get('minecraft', 'home'), self.application.process_prefix + server_id)).edit_address(self.get_argument('address'))
                    change_requiring_restart = True
                elif server.Type == "bukkit":
                    Bukkit(os.path.join(self.application.config.get('minecraft', 'home'), self.application.process_prefix + server_id)).edit_port(int(self.get_argument('port')))
                    Bukkit(os.path.join(self.application.config.get('minecraft', 'home'), self.application.process_prefix + server_id)).edit_address(self.get_argument('address'))
                    change_requiring_restart = True
                else:
                    Base(os.path.join(self.application.config.get('minecraft', 'home'), self.application.process_prefix + server_id)).edit_port(int(self.get_argument('port')))
                    Base(os.path.join(self.application.config.get('minecraft', 'home'), self.application.process_prefix + server_id)).edit_address(self.get_argument('address'))
                    change_requiring_restart = True
                self.application.db.edit_port(server_id, int(self.get_argument('port')))
                self.application.db.edit_address(server_id, self.get_argument('address'))
            else:
                error = True
                message = 'That IP/Port allocation has been taken'

        if int(self.get_argument('memory')) != server.Memory and not error:
            memory = int(self.get_argument('memory')) # dodgy input validation, it's possible to screw up the config really bad if something other than a number comes in!
            self.application.supervisor.edit_memory(self.application.process_prefix + server_id, os.path.dirname(self.application.supervisor_config_path), memory)
            self.application.db.edit_memory(server_id, memory)
            change_requiring_restart = True

        if change_requiring_restart and self.application.supervisor.is_process_running(self.application.process_prefix + server_id):
            self.application.supervisor.run_command(self.application.process_prefix + server_id, 'stop')
            self.callback = tornado.ioloop.PeriodicCallback(self.stop_server, 1000)
            self.callback.start()
            message = "Changes applied successfully. If a restart is required, the server will safely stop and start in the background now."
            error = False

        self.render(self.application.settings['template_path'] + '/servers/server/settings.template', server_id=server_id, message=message, error=error, interfaces=interfaces)


    def stop_server(self):
        if not self.application.supervisor.is_process_running(self.application.process_prefix + self.server_id):
            self.application.supervisor.refresh(self.application.process_prefix + self.server_id)
            self.callback.stop()


class Update(BaseServerHandler):
    @asynchronous
    @authenticated
    def get(self, server_id):
        self.render(self.application.settings['template_path'] + '/servers/server/update.template', server_id=server_id)