__author__ = 'brayden'

from peewee import *
import passlib.hash
from Config import config
from tornado.web import escape
import os


class Database():
    class UnsupportedDatabaseType(Exception):
        message = 'The database specified in the configuration is not a supported type.\r\n' \
                  'Available types are: sqlite, mysql and postgresql.'

    def __init__(self):
        self.config = config()
        self.rounds = 20000
        create_db = False
        if self.config.get('database', 'type') == 'sqlite':
            if not os.path.exists(self.config.get('database', 'host')):
                print "Database is not populated. Initialising.."
                create_db = True
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
            Username = CharField(null=False, unique=True, max_length=64, primary_key=True)
            Password = CharField(null=False, max_length=76)  # Length of what sha1_crypt produces
            API_Key = CharField(null=True, default=None, unique=True, max_length=128)  # SHA256
            Session = CharField(null=True, max_length=128, default=None)  # SHA256
            Is_Admin = BooleanField(default=False)

            class Meta:
                database = self.database

        class Servers(Model):
            ID = PrimaryKeyField()
            Address = CharField(max_length=39, null=False)
            Port = IntegerField(null=False)
            Owner = CharField(null=False, max_length=64)
            Memory = IntegerField(null=False)  # int as MB, translated to <memory>MB in start command
            ServerJar = CharField(max_length=128, null=False)
            Type = CharField(max_length=128, null=False)  # craftbukkit, minecraft, etc.
            Stream = CharField(null=False, max_length=128)  # rb, dev, beta etc.
            Is_Active = BooleanField(default=False)  # to get around a weird issue with sqlite and autoincrement, always make unique IDs, keep them unique regardless! mysql's default behaviour makes this a non-issue but sqlite :(

            class Meta:
                database = self.database

        class Backup_Destinations(Model):
            ID = PrimaryKeyField()
            FriendlyName = CharField(max_length=255, null=False, unique=False)
            Type = CharField(max_length=128, null=False) # The method used for backing, e.g.: zip, rdiff-backup etc.
            Folder = TextField(null=False) # if local then local folder, remote then remote folder etc.
            Host = CharField(max_length=255, null=True, default=None) # if remote, then this is the host to use, as defined in ~/.ssh/config, which will contain private key, public key, hostname, port etc.
            # private key is required for passwordless authentication, passwords are a bad idea and NOT supported.
            Remote = BooleanField(null=False, default=False)

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
            PermissionKey = CharField(null=False, unique=True, max_length=128)

            class Meta:
                database = self.database

        class Role_Permissions(Model):  # Assign permissions to roles
            ID = PrimaryKeyField()
            Role_ID = IntegerField(null=False)
            Permission_ID = IntegerField(null=False)

            class Meta:
                database = self.database

        class User_Roles(Model):  # Assign role to users per server
            ID = PrimaryKeyField()
            User_ID = IntegerField(null=False)
            Role_ID = IntegerField(null=False)
            Server_ID = IntegerField(null=False)

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
        self.Backup_Destinations = Backup_Destinations

        if create_db:
            self.initialiseDatabase()
            self.add_user('Admin', 'admin', True)
            print "Database initialised. Login is: \r\nUsername: Admin\r\nPassword: admin"

    def initialiseDatabase(self):  # if param is true it'll suppress errors
        self.Servers.create_table(True)
        self.Users.create_table(True)
        self.Roles.create_table(True)
        self.Permissions.create_table(True)
        self.Role_Permissions.create_table(True)
        self.User_Roles.create_table(True)
        self.Backup_Destinations(True)

    def add_user(self, username, password, is_admin=False):
        password = passlib.hash.sha1_crypt.encrypt(password, rounds=self.rounds)
        self.Users.create(Username=escape.xhtml_escape(username), Password=password, Is_Admin=is_admin, force_insert=True)

    def add_server(self, address, port, memory, owner, stream, server_type="craftbukkit"):
        self.Servers.create(Address=address, Port=port, Memory=memory, Owner=owner, ServerJar='minecraft.jar', Type=server_type, Stream=stream, Is_Active=True)

    def get_servers(self):
        return self.Servers.select().where(self.Servers.Is_Active == True)

    def get_server(self, server_id):
        return self.Servers.select().where(self.Servers.ID == server_id, self.Servers.Is_Active == True).get()

    def server_exists(self, server_id):
        try:
            self.Servers.select().where(self.Servers.ID == server_id, self.Servers.Is_Active == True).get()
            return True
        except DoesNotExist:
            return False

    def get_server_id(self, address, port):
        return self.Servers.select().where(self.Servers.Address == address, self.Servers.Port == port, self.Servers.Is_Active == True).get().ID

    def is_address_taken(self, address, port):
        try:
            if address == '0.0.0.0':
                self.Servers.select().where(self.Servers.Port == port, self.Servers.Is_Active == True).get()
            else:
                self.Servers.select().where(self.Servers.Address == address, self.Servers.Port == port, self.Servers.Is_Active == True).get()
            return True
        except DoesNotExist:
            return False

    def insert_session(self, username, session):
        self.Users.update(Session=session).where(self.Users.Username == username).execute()

    def ping(self):
        self.database.execute_sql('/* ping */ SELECT 1')  # Ping the database

    def get_session(self, username):
        return self.Users.select(self.Users.Session).where(self.Users.Username == username).get().Session

    def check_credentials(self, username, password):
        passwordHash = self.Users.select(self.Users.Password).where(self.Users.Username == username).get().Password
        return passlib.hash.sha1_crypt.verify(password, passwordHash)

    def add_role(self, role_name):
        self.Roles.create(RoleName=role_name)

    def assign_perm_to_role(self, perm_id, role_id):
        self.Role_Permissions.create(Role_ID=role_id, Permission_ID=perm_id)

    def assign_user_to_role(self, user, role_id):
        self.User_Roles.update(Role_ID=role_id, User_ID=user).execute()

    def get_roles(self):
        return self.Roles.select()

    def get_role_permissions(self, role_id):
        return self.Role_Permissions().where(self.Role_Permissions.Role_ID == role_id).get()

    def is_user_admin(self, user):
        return self.Users.select(self.Users.Is_Admin).where(self.Users.Username == user).get().Is_Admin

    def get_users(self):
        return self.Users.select()

    def delete_user(self, user):
        (self.Users.get(self.Users.Username == user)).delete_instance()

    def delete_server(self, server_id):
        self.Servers.update(Is_Active = False).where(self.Servers.ID == server_id).execute()

    def edit_user(self, username, password=None, api_key=None, session=None, is_admin=None):
        user = self.Users()
        user.Username = username
        if type(password) is unicode:
            user.Password = passlib.hash.sha1_crypt.encrypt(password, rounds=self.rounds)
        if type(api_key) is unicode:
            user.API_Key = api_key
        if type(session) is unicode:
            user.Session = session
        if type(is_admin) is bool:
            user.Is_Admin = is_admin

        user.save()

    def change_password(self, username, new_password):
        self.Users.update(Password=passlib.hash.sha1_crypt.encrypt(new_password, rounds=self.rounds)).where(self.Users.Username == username).execute()