__author__ = 'brayden'

import tornado.web
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


class Application(tornado.web.Application):
    def __init__(self):
        self.config = config()
        self.db = Database.database.Database()
        self.sessionCache = {}
        self.title = self.config.get('panel', 'title')
        self.name = self.config.get('panel', 'name')
        self.usernames = {} # has some info about user, like is_admin etc. just to save useless SQL stuff
        self.generateUsernameCache()
        self.supervisorAuth = {'Username': '', 'Password': ''}
        self.parseSupervisorConfig()
        self.supervisor = Supervisor(self.supervisorAuth['Username'], self.supervisorAuth['Password'])
        handlers = [
            ('Home', r'/', IndexHandler),
            ('Login', r'/login', LoginHandler),
            ('PerformLogin', r'/ajax/performLogin', PerformLoginHandler),
            ('Logout', r'/logout', LogoutHandler),
            ('Admin_Home', r'/admin/', AdminIndex),
            ('Admin_Users', r'/admin/users', AdminUsers),
            ('Admin_Roles', r'/admin/roles', AdminRoles),
            ('Admin_Ajax_GetUsers', r'/admin/ajax/getUsers', GetUserHandler),
            ('Admin_Ajax_AddUser', r'/admin/ajax/addUser', AddUserHandler),
            ('Admin_Ajax_DeleteUser', r'/admin/ajax/deleteUser', DeleteUserHandler),
            ('Admin_Ajax_EditUser', r'/admin/ajax/editUser', EditUserHandler),
            ('Servers_Index', r'/servers/', ServersIndexHandler),
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
        print self.named_handlers

    def acl(self, required_access, current_user, server_id):
        user_perms = ['test', 'perm1']
        for access in user_perms:
            if access in required_access:
                break
        else:
            raise tornado.web.HTTPError(403)

    def makeSession(self, username):
        session = hashlib.sha256(os.urandom(32)).hexdigest()
        self.sessionCache[username] = session
        self.db.insertSession(username, session)
        return session

    def checkSession(self, username, session):
        if 'username' in self.sessionCache:
            if self.sessionCache[username] == session:
                return True
            else:
                return False
        else:  # not cached, due to daemon restart? fallback onto more expensive method
            if self.db.getSession(username) == session:
                self.sessionCache[username] = session  # push it into the cache
                return True
            else:
                return False

    def dbPing(self):
        self.db.ping()

    def generateUsernameCache(self):
        users = self.db.getUsers()
        for user in users:
            self.usernames[user.Username] = {'Is_Admin': user.Is_Admin}

    def parseSupervisorConfig(self):
        config = ConfigParser.RawConfigParser()
        config.read('/etc/supervisor/supervisord.conf')
        self.supervisorAuth['Username'] = config.get('inet_http_server', 'username')
        self.supervisorAuth['Password'] = config.get('inet_http_server', 'password')