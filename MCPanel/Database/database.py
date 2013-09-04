__author__ = 'brayden'

from peewee import *
import passlib.hash
from MCPanel.Config import config


class Database():
    class UnsupportedDatabaseType(Exception):
        message = 'The database specified in the configuration is not a supported type.\r\n' \
                  'Available types are: sqlite, mysql and postgresql.'

    def __init__(self):
        self.config = config()
        if self.config.get('database', 'type') == 'sqlite':
            self.database = SqliteDatabase(self.config.get('database', 'host'))
            self.database.connect()
        elif self.config.get('database', 'type') == 'mysql':
            self.database = MySQLDatabase(self.config.get('database', 'database'),
                                          user=self.config.get('database', 'user'),
                                          passwd=self.config.get('database', 'password'),
                                          host=self.config.get('database', 'host'))
            self.database.connect()
        elif self.config.get('database', 'type') == 'postgresql':
            self.database = PostgresqlDatabase(self.config.get('database', 'database'),
                                               user=self.config.get('database', 'user'),
                                               passwd=self.config.get('database', 'password'),
                                               host=self.config.get('database', 'host'))
            self.database.connect()
        else:
            raise self.UnsupportedDatabaseType()

        class Users(Model):
            #ID = PrimaryKeyField()  # can't be set if I want to do a foreign key relationship
            Username = CharField(null=False, unique=True, max_length=255)
            Password = CharField(null=False, max_length=76)  # Length of what sha1_crypt produces
            API_Key = CharField(null=True, default=None, unique=True, max_length=128)  # SHA256
            Session = CharField(null=True, max_length=128, default=None)  # SHA256
            Is_Admin = BooleanField(default=False)

            class Meta:
                database = self.database

        class Servers(Model):
            ID = PrimaryKeyField()
            ServerName = CharField(null=False, max_length=255)
            Address = CharField(max_length=39)
            Port = IntegerField()

            class Meta:
                database = self.database

        class Roles(Model):  # Stores role name and ID used to reference it later
            ID = PrimaryKeyField()
            RoleName = CharField(null=False, max_length=128)

            class Meta:
                database = self.database

        class Permissions(Model):  # Stores the name of permissions and a key for referencing them.
                                   # Name is friendly name for the permission
            ID = PrimaryKeyField()
            PermissionName = CharField(null=False, max_length=128)
            PermissionKey = CharField(null=False, max_length=128)

            class Meta:
                database = self.database

        class Role_Permissions(Model):  # Assign permissions to roles
            ID = PrimaryKeyField()
            Role_ID = IntegerField(null=False)
            Permission_ID = IntegerField(null=False)

            class Meta:
                database = self.database

        class User_Roles(Model):  # Assign role to users.
            ID = PrimaryKeyField()
            User = ForeignKeyField(Users, null=False, related_name='ID')
            Role_ID = IntegerField(null=False)

            class Meta:
                database = self.database

        # The ACL stuff is copied to a large extent from http://stackoverflow.com/a/10311479/2077881
        # This is the first time I've implemented an ACL system so posts such as those are extremely helpful for
        # identifying best practice.

        self.database.autocommit = True
        self.Servers = Servers
        self.Users = Users
        self.Roles = Roles
        self.Permissions = Permissions
        self.Role_Permissions = Role_Permissions
        self.User_Roles = User_Roles

    def initialiseDatabase(self):  # if param is true it'll suppress errors
        self.Servers.create_table(True)
        self.Users.create_table(True)
        self.Roles.create_table(True)
        self.Permissions.create_table(True)
        self.Role_Permissions.create_table(True)
        self.User_Roles.create_table(True)

    def addUser(self, username, password, is_admin=False):
        password = passlib.hash.sha1_crypt.encrypt(password, rounds=20000)
        self.Users.create(Username=username, Password=password, Is_Admin=is_admin, force_insert=True)

    def insertSession(self, username, session):
        self.Users.update(Session=session).where(self.Users.Username == username).execute()

    def ping(self):
        self.database.execute_sql('/* ping */ SELECT 1')  # Ping the database

    def getSession(self, username):
        return self.Users.select(self.Users.Session).where(self.Users.Username == username).get().Session

    def checkCredentials(self, username, password):
        passwordHash = self.Users.select(self.Users.Password).where(self.Users.Username == username).get().Password
        return passlib.hash.sha1_crypt.verify(password, passwordHash)

    def addRole(self, roleName):
        self.Roles.create(RoleName=roleName)

    def assignPermToRole(self, perm_id, role_id):
        self.Role_Permissions.create(Role_ID=role_id, Permission_ID=perm_id)

    def assignUserToRole(self, user, role_id):
        if type(user) is str:  # assume user is name and not ID and look up ID as a result
            user = self.Users.select(self.Users.id).where(self.Users.Username == user).get().id

        self.User_Roles.update(Role_ID=role_id, User_ID=user).execute()