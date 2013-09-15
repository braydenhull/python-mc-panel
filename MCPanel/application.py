__author__ = 'brayden'

import tornado.web
import tornado
import os
import hashlib
import MCPanel.Database.database
from Config import config
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


class Application(tornado.web.Application):
    def __init__(self):
        self.config = config()
        self.db = MCPanel.Database.database.Database()
        self.sessionCache = {}
        self.title = self.config.get('panel', 'title')
        self.name = self.config.get('panel', 'name')
        handlers = [
            (r'/', IndexHandler),
            (r'/login', LoginHandler),
            (r'/ajax/performLogin', PerformLoginHandler),
            (r'/logout', LogoutHandler),
            (r'/admin/', AdminIndex),
            (r'/admin/users', AdminUsers),
            (r'/admin/roles', AdminRoles),
            (r'/admin/ajax/getUsers', GetUserHandler),
            (r'/admin/ajax/addUser', AddUserHandler),
            (r'/admin/ajax/deleteUser', DeleteUserHandler),
            (r'/admin/ajax/editUser', EditUserHandler),
        ]
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