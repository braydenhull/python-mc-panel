__author__ = 'brayden'

import tornado
import os
import hashlib
import Database.database
import ConfigParser
from tornado.web import URLSpec
from Config import config
from Minecraft.supervisor import Supervisor
from Handlers.Index import IndexHandler
from Handlers.Login import LoginHandler
from Handlers.Ajax.PerformLogin import PerformLoginHandler
from Handlers.Logout import LogoutHandler
from Handlers.Admin.Index import AdminIndex
from Handlers.Admin.Users import AdminUsers
from Handlers.Admin.Roles import AdminRoles
from Handlers.Admin.Ajax.GetUsers import GetUserHandler
from Handlers.Admin.Ajax.AddUser import AddUserHandler
from Handlers.Admin.Ajax.DeleteUser import DeleteUserHandler
from Handlers.Admin.Ajax.EditUser import EditUserHandler
from Handlers.Servers.Index import ServersIndexHandler
from Handlers.Servers.Server.Index import ServerIndexHandler
from Handlers.Servers.Server.Players import ServerPlayersHandler
from Handlers.Servers.WebSocket.CreateServer import CreateServerHandler
from Handlers.Servers.Ajax.CheckAddress import CheckAddressHandler
from Handlers.Servers.Ajax.GetInfo import GetInfoHandler
from Handlers.Servers.Server.Console import ServerConsoleHandler
from Handlers.Servers.Server.Ajax.GetLog import GetLogHandler
from Handlers.Servers.Server.Ajax.SendCommand import SendCommandHandler
from Handlers.Servers.Server.Properties import ServerPropertiesHandler
from Handlers.Servers.Ajax.DeleteServer import DeleteServerHandler
from Handlers.Servers.Server.Ajax.GetPlayers import GetPlayersHandler
from Handlers.Servers.Server.Ajax.KickPlayer import KickPlayerHandler
from Handlers.Servers.Server.Ajax.BanPlayer import BanPlayerHandler
from Handlers.Servers.Server.Ajax.GetBannedPlayers import GetBannedPlayersHandler
from Handlers.Servers.Server.Ajax.UnbanPlayer import UnbanPlayerHandler
from Handlers.Servers.Server.Ajax.GetOperators import GetOperatorsHandler
from Handlers.Servers.Server.Ajax.OpPlayer import OpPlayerHandler
from Handlers.Servers.Server.Ajax.DeopPlayer import DeopPlayerHandler


class Application(tornado.web.Application):
    def __init__(self):
        self.config = config()
        self.db = Database.database.Database()
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
        self.supervisor = Supervisor(self.supervisor_auth['Username'], self.supervisor_auth['Password'])
        handlers = [
            ('Home', r'/', IndexHandler),
            ('Login', r'/login', LoginHandler),
            ('PerformLogin', r'/ajax/performLogin', PerformLoginHandler),
            ('Logout', r'/logout', LogoutHandler),
            ('Admin_Home', r'/admin/?', AdminIndex),
            ('Admin_Users', r'/admin/users', AdminUsers),
            ('Admin_Roles', r'/admin/roles', AdminRoles),
            ('Admin_Ajax_GetUsers', r'/admin/ajax/getUsers', GetUserHandler),
            ('Admin_Ajax_AddUser', r'/admin/ajax/addUser', AddUserHandler),
            ('Admin_Ajax_DeleteUser', r'/admin/ajax/deleteUser', DeleteUserHandler),
            ('Admin_Ajax_EditUser', r'/admin/ajax/editUser', EditUserHandler),
            ('Servers_Index', r'/servers/?', ServersIndexHandler),
            ('Server_Index', r'/servers/(\d+)/', ServerIndexHandler),
            ('Server_Players', r'/servers/(\d+)/players', ServerPlayersHandler),
            ('Servers_WebSocket_CreateServer', r'/servers/websocket/createserver', CreateServerHandler),
            ('Servers_Ajax_CheckAddress', r'/servers/ajax/checkAddress', CheckAddressHandler),
            ('Servers_Ajax_GetInfo', r'/servers/ajax/getInfo', GetInfoHandler),
            ('Server_Console', r'/servers/(\d+)/console', ServerConsoleHandler),
            ('Server_Ajax_GetLog', r'/servers/(\d+)/ajax/getLog', GetLogHandler),
            ('Server_Ajax_SendCommand', r'/servers/(\d+)/ajax/sendCommand', SendCommandHandler),
            ('Server_Properties', r'/servers/(\d+)/properties', ServerPropertiesHandler),
            ('Servers_DeleteServer', r'/servers/deleteServer', DeleteServerHandler),
            ('Server_Ajax_GetPlayers', r'/servers/(\d+)/ajax/getPlayers', GetPlayersHandler),
            ('Server_Ajax_KickPlayer', r'/servers/(\d+)/ajax/kickPlayer', KickPlayerHandler),
            ('Server_Ajax_BanPlayer', r'/servers/(\d+)/ajax/banPlayer', BanPlayerHandler),
            ('Server_Ajax_GetBannedPlayers', r'/servers/(\d+)/ajax/getBannedPlayers', GetBannedPlayersHandler),
            ('Server_Ajax_UnbanPlayer', r'/servers/(\d+)/ajax/unbanPlayer',  UnbanPlayerHandler),
            ('Server_Ajax_GetOperators', r'/servers/(\d+)/ajax/getOperators', GetOperatorsHandler),
            ('Server_Ajax_OpPlayer', r'/servers/(\d+)/ajax/opPlayer', OpPlayerHandler),
            ('Server_Ajax_DeopPlayer', r'/servers/(\d+)/ajax/deopPlayer', DeopPlayerHandler),
        ]
        handlers = [URLSpec(pattern, handler, name=name) for name, pattern, handler in handlers]
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

    def make_session(self, username):
        session = hashlib.sha256(os.urandom(32)).hexdigest()
        self.session_cache[username] = session
        self.db.insertSession(username, session)
        return session

    def check_session(self, username, session):
        if 'username' in self.session_cache:
            if self.session_cache[username] == session:
                return True
            else:
                return False
        else:  # not cached, due to daemon restart? fallback onto more expensive method
            if self.db.getSession(username) == session:
                self.session_cache[username] = session  # push it into the cache
                return True
            else:
                return False

    def db_ping(self):
        self.db.ping()

    def generate_username_cache(self):
        users = self.db.getUsers()
        for user in users:
            self.usernames[user.Username] = {'Is_Admin': user.Is_Admin}

    def parse_supervisor_config(self):
        config = ConfigParser.RawConfigParser()
        config.read(self.supervisor_config_path)
        self.supervisor_auth['Username'] = config.get('inet_http_server', 'username')
        self.supervisor_auth['Password'] = config.get('inet_http_server', 'password')