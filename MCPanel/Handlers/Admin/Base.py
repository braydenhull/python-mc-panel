__author__ = 'brayden'

from ..Base import BaseHandler
from tornado.web import HTTPError
from peewee import DoesNotExist


class BaseAdminHandler(BaseHandler):
    pass
    # def prepare(self): # not necessary now with the decorator
    #     self.if_admin()