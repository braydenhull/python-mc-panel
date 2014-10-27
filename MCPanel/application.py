__author__ = 'brayden'

import tornado
import os
import hashlib
import Libs.database
import Libs.authentication
import Libs.log
import ConfigParser
import json
from tornado.web import URLSpec
from Config import config
from Minecraft.supervisor import Supervisor
import Handlers
import Handlers.Home
import Handlers.Ajax
import Handlers.Ajax.PerformLogin
import Handlers.Admin.AdminController
import Handlers.Admin.Ajax.UserController
import Handlers.Servers.Index
import Handlers.Servers.WebSocket.CreateServer
import Handlers.Servers.Ajax.CheckAddress
import Handlers.Servers.Ajax.GetInfo
import Handlers.Servers.Server.Ajax.GetLog
import Handlers.Servers.Server.Ajax.SendCommand
import Handlers.Servers.Server.Ajax.PlayerController
import Handlers.User.Index
import Handlers.Servers.Ajax.ServerController
import Handlers.Servers.Server.Ajax.Update
import Handlers.Servers.Server.Ajax.GetProcessInfo
import Handlers.Servers.Server.WebSocket.LogController
import Handlers.System.BackupDestinations
import Handlers.System.Backup.Index
import Handlers.System.Backup.Ajax.DeleteBackup
import Handlers.Servers.Server.Ajax.BackupServer
import Handlers.Servers.Server.Ajax.DeleteBackup
import Handlers.Servers.Server.ServerController


class Application(tornado.web.Application):
    def __init__(self):
        self.config = config()
        self.db = Libs.database.Database()
        self.authentication = Libs.authentication.Authentication(self)
        self.log = Libs.log.Log()
        self.session_cache = {}
        self.title = self.config.get('panel', 'title')
        self.name = self.config.get('panel', 'name')
        self.supervisor_config_path = self.config.get('supervisor', 'configuration')
        self.usernames = {}  # has some info about user, like is_admin etc. just to save useless SQL stuff
        self.generate_username_cache()
        self.supervisor_auth = {'Username': '', 'Password': ''}
        self.parse_supervisor_config()
        self.process_prefix = "minecraft_"
        self.craftbukkit_build_list = {}
        self.vanilla_build_list = {}
        self.supervisor = Supervisor(self.supervisor_auth['Username'], self.supervisor_auth['Password'])
        self.setup_bukkit_jar_cache()
        self.setup_vanilla_jar_cache()
        self.vanilla_builds = {}
        handlers = [
            ('Home', r'/', Handlers.Home.IndexHandler, {'title': 'Home'}),
            ('Login', r'/login', Handlers.Home.LoginHandler, {'title': 'Login'}),
            ('PerformLogin', r'/ajax/performLogin', Handlers.Ajax.PerformLogin.PerformLoginHandler, {'title': None}),
            ('Logout', r'/logout', Handlers.Home.LogoutHandler, {'title': 'Logout'}),
            ('Admin_Home', r'/admin/?', Handlers.Admin.AdminController.Index, {'title': 'Admin Home'}),
            ('Admin_Users', r'/admin/users', Handlers.Admin.AdminController.Users, {'title': 'User Management'}),
            ('Admin_Roles', r'/admin/roles', Handlers.Admin.AdminController.Roles, {'title': 'Role Management'}),
            ('Admin_Ajax_GetUsers', r'/admin/ajax/getUsers', Handlers.Admin.Ajax.UserController.GetUser, {'title': None}),
            ('Admin_Ajax_AddUser', r'/admin/ajax/addUser', Handlers.Admin.Ajax.UserController.AddUser, {'title': None}),
            ('Admin_Ajax_DeleteUser', r'/admin/ajax/deleteUser', Handlers.Admin.Ajax.UserController.DeleteUser, {'title': None}),
            ('Admin_Ajax_EditUser', r'/admin/ajax/editUser', Handlers.Admin.Ajax.UserController.EditUser, {"title": None}),
            ('Servers_Index', r'/servers/?', Handlers.Servers.Index.ServersIndexHandler, {"title": "Servers"}),
            ('Server_Index', r'/servers/(\d+)/', Handlers.Servers.Server.ServerController.Index, {"title": "Server"}),
            ('Server_Players', r'/servers/(\d+)/players', Handlers.Servers.Server.ServerController.Players, {'title': 'Server Players'}),
            ('Servers_WebSocket_CreateServer', r'/servers/websocket/createServer', Handlers.Servers.WebSocket.CreateServer.CreateServerHandler, {'title': None}),
            ('Servers_Ajax_CheckAddress', r'/servers/ajax/checkAddress', Handlers.Servers.Ajax.CheckAddress.CheckAddressHandler, {'title': None}),
            ('Servers_Ajax_GetInfo', r'/servers/ajax/getInfo', Handlers.Servers.Ajax.GetInfo.GetInfoHandler, {'title': None}),
            ('Server_Console', r'/servers/(\d+)/console', Handlers.Servers.Server.ServerController.Console, {'title': 'Server Console'}),
            ('Server_Ajax_GetLog', r'/servers/(\d+)/ajax/getLog', Handlers.Servers.Server.Ajax.GetLog.GetLogHandler, {'title': None}),
            ('Server_Ajax_SendCommand', r'/servers/(\d+)/ajax/sendCommand', Handlers.Servers.Server.Ajax.SendCommand.SendCommandHandler, {'title': None}),
            ('Server_Properties', r'/servers/(\d+)/properties', Handlers.Servers.Server.ServerController.Properties, {'title': 'Server Properties'}),
            ('Servers_DeleteServer', r'/servers/ajax/deleteServer', Handlers.Servers.Ajax.ServerController.DeleteServer, {'title': None}),
            ('Server_Ajax_GetPlayers', r'/servers/(\d+)/ajax/getPlayers', Handlers.Servers.Server.Ajax.PlayerController.GetPlayers, {'title': None}),
            ('Server_Ajax_KickPlayer', r'/servers/(\d+)/ajax/kickPlayer', Handlers.Servers.Server.Ajax.PlayerController.KickPlayer, {'title': None}),
            ('Server_Ajax_BanPlayer', r'/servers/(\d+)/ajax/banPlayer', Handlers.Servers.Server.Ajax.PlayerController.BanPlayer, {'title': None}),
            ('Server_Ajax_GetBannedPlayers', r'/servers/(\d+)/ajax/getBannedPlayers', Handlers.Servers.Server.Ajax.PlayerController.GetBannedPlayers, {'title': None}),
            ('Server_Ajax_UnbanPlayer', r'/servers/(\d+)/ajax/unbanPlayer',  Handlers.Servers.Server.Ajax.PlayerController.UnbanPlayer, {'title': None}),
            ('Server_Ajax_GetOperators', r'/servers/(\d+)/ajax/getOperators', Handlers.Servers.Server.Ajax.PlayerController.GetOperators, {'title': None}),
            ('Server_Ajax_OpPlayer', r'/servers/(\d+)/ajax/opPlayer', Handlers.Servers.Server.Ajax.PlayerController.OpPlayer, {'title': None}),
            ('Server_Ajax_DeopPlayer', r'/servers/(\d+)/ajax/deopPlayer', Handlers.Servers.Server.Ajax.PlayerController.DeopPlayer, {'title': None}),
            ('User_Index', r'/user/?', Handlers.User.Index.UserIndexHandler, {'title': 'User Settings'}),
            ('Servers_Ajax_StartServer', r'/servers/ajax/startServer', Handlers.Servers.Ajax.ServerController.StartServer, {'title': None}),
            ('Servers_Ajax_StopServer', r'/servers/ajax/stopServer', Handlers.Servers.Ajax.ServerController.StopServer, {'title': None}),
            ('Server_Update', r'/servers/(\d+)/update', Handlers.Servers.Server.ServerController.Update, {'title': 'Server Update'}),
            ('Server_Ajax_Update', r'/servers/(\d+)/ajax/update', Handlers.Servers.Server.Ajax.Update.UpdateServerHandler, {'title': None}),
            ('Server_Ajax_GetProcessInfo', r'/servers/(\d+)/ajax/getProcessInfo', Handlers.Servers.Server.Ajax.GetProcessInfo.GetProcessInfoHandler, {'title': None}),
            ('Server_WebSocket_GetLog', r'/servers/(\d+)/websocket/getLog', Handlers.Servers.Server.WebSocket.LogController.GetLog, {'title': None}),
            ('Server_Backup', r'/servers/(\d+)/backup', Handlers.Servers.Server.ServerController.Backup, {'title': 'Server Backup'}),
            ('System_BackupDestinations', r'/system/backup', Handlers.System.BackupDestinations.SystemBackupDestinationsHandler, {'title': 'Backup Destinations'}),
            ('System_Backup_Index', r'/system/backup/(\d+)/', Handlers.System.Backup.Index.BackupIndexHandler, {'title': 'Backup Destination Index'}),
            ('System_Backup_Ajax_DeleteBackup', r'/system/backup/(\d+)/ajax/deleteBackup', Handlers.System.Backup.Ajax.DeleteBackup.DeleteBackupHandler, {'title': None}),
            ('Server_Ajax_BackupServer', r'/servers/(\d+)/ajax/backupServer', Handlers.Servers.Server.Ajax.BackupServer.BackupServerHandler, {'title': None}),
            ('Server_Ajax_DeleteBackup', r'/servers/(\d+)/ajax/deleteBackup', Handlers.Servers.Server.Ajax.DeleteBackup.DeleteBackupHandler, {'title': None}),
            ('Server_Settings', r'/servers/(\d+)/settings', Handlers.Servers.Server.ServerController.Settings, {'title': 'Server Settings'}),
        ]
        handlers = [URLSpec(pattern, handler, name=name, kwargs=kwargs) for name, pattern, handler, kwargs in handlers]
        settings = dict(
            debug=True,
            gzip=True,
            login_url='/login',
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

    def acl(self, required_access, current_user, server_id):
        user_perms = ['test', 'perm1']
        for access in user_perms:
            if access in required_access:
                break
        else:
            raise tornado.web.HTTPError(403)

    def db_ping(self):
        self.db.ping()

    def generate_username_cache(self):
        users = self.authentication.get_users()
        for user in users:
            self.usernames[user.Username] = {'Is_Admin': user.Is_Admin}

    def parse_supervisor_config(self):
        supervisord_config = ConfigParser.RawConfigParser()
        supervisord_config.read(self.supervisor_config_path)
        self.supervisor_auth['Username'] = supervisord_config.get('inet_http_server', 'username')
        self.supervisor_auth['Password'] = supervisord_config.get('inet_http_server', 'password')

    def setup_bukkit_jar_cache(self):
        directory = os.path.dirname(self.config.config_file)
        if not os.path.exists(directory + '/bukkit_jar_cache/'):
            os.mkdir(directory + '/bukkit_jar_cache/')

        if not os.path.exists(directory + '/bukkit_jar_cache/versions.json'):
            with open(directory + '/bukkit_jar_cache/versions.json', 'w') as f:
                json.dump({'builds': {}}, f)

    def setup_vanilla_jar_cache(self):
        directory = os.path.dirname(self.config.config_file)
        if not os.path.exists(directory + '/vanilla_jar_cache/'):
            os.mkdir(directory + '/vanilla_jar_cache/')

        if not os.path.exists(directory + '/vanilla_jar_cache/versions.json'):
            with open(directory + '/vanilla_jar_cache/versions.json', 'w') as f:
                json.dump({'builds': {}}, f)