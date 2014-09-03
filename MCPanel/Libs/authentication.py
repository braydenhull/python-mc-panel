__author__ = 'brayden'

from peewee import DoesNotExist
import passlib.hash
from tornado.escape import xhtml_escape
import hashlib
import os


class Authentication:
    def __init__(self, application):
        self.application = application
        self.rounds = 1000

    class InvalidUser(Exception):
        def __init__(self, message):
            self.message = message

    def _get_users(self):
        return self.application.db.Users.select()

    def get_users(self):
        return self._get_users()

    def _get_user(self, username):
        try:
            return self.application.db.Users.select().where(self.application.db.Users.Username == username).get()
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)

    def add_user(self, username, password, is_admin=False):
        password = passlib.hash.sha1_crypt.encrypt(password, rounds=self.rounds)
        self.application.db.Users.create(Username=xhtml_escape(username), Password=password, Is_Admin=is_admin, force_insert=True)

    def _generate_session(self):
        return hashlib.sha256(os.urandom(32)).hexdigest()

    def _insert_session(self, username):
        session = self._generate_session()
        try:
            self.application.db.Users.update(Session=session).where(self.application.db.Users.Username == username).execute()
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)
        self.application.session_cache[username] = session
        return session

    def make_session(self, username):
        return self._insert_session(username)

    def _get_session(self, username):
        if username in self.application.session_cache:
            return self.application.session_cache[username]
        else:
            try:
                session = self.application.db.Users.select(self.application.db.Users.Session).where(self.application.db.Users.Username == username).get().Session
            except DoesNotExist:
                raise self.InvalidUser('Given username could not be found, %s' % username)
            self.application.session_cache[username] = session
        return session

    def _check_session(self, username, session):
        if username in self.application.session_cache:
            if self.application.session_cache[username] == session:
                return True
            else:
                return False
        else:
            if self._get_session(username) == session:
                self.application.session_cache[username] = session
                return True
            else:
                return False

    def check_session(self, username, session):
        return self._check_session(username, session)

    def _check_credentials(self, username, password):
        try:
            password_hash = self.application.db.Users.select(self.application.db.Users.Password).where(self.application.db.Users.Username == username).get().Password
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)
        return passlib.hash.sha1_crypt.verify(password, password_hash)

    def check_credentials(self, username, password):
        return self._check_credentials(username, password)

    def _is_user_admin(self, username):
        try:
            return self.application.db.Users.select(self.application.db.Users.Is_Admin).where(self.application.db.Users.Username == username).get().Is_Admin
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)

    def is_user_admin(self, username):
        return self._is_user_admin(username)

    def _delete_user(self, username):
        try:
            (self.application.db.Users.get(self.application.db.Users.Username == username)).delete_instance()
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)

    def delete_user(self, username):
        self._delete_user(username)

    def _set_admin(self, username, is_admin):
        try:
            self.application.db.Users.update(Is_Admin=is_admin).where(self.application.db.Users.Username == username).execute()
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)

    def set_admin(self, username, is_admin):
        self._set_admin(username, is_admin)

    def _generate_api_key(self):
        return hashlib.sha256(os.urandom(32))

    def _set_api_key(self, username):
        try:
            key = self._generate_api_key()
            self.application.db.Users.update(API_Key=key).where(self.application.db.Users.Username == username).execute()
            return key
        except DoesNotExist:
            raise self.InvalidUser('Given username could not be found, %s' % username)

    def set_api_key(self, username):
        return self._set_api_key(username)

    def _change_password(self, username, password):
        self.application.db.Users.update(Password=passlib.hash.sha1_crypt.encrypt(password, rounds=self.rounds)).where(self.application.db.Users.Username == username).execute()

    def change_password(self, username, password):
        self._change_password(username, password)