__author__ = 'brayden'

from ..Base import BaseHandler
from tornado.web import HTTPError
from peewee import DoesNotExist


class BaseAdminHandler(BaseHandler):
    def prepare(self):
        self.if_admin()