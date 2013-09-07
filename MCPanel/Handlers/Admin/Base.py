__author__ = 'brayden'

from MCPanel.Handlers.Base import BaseHandler
from tornado.web import HTTPError
from peewee import DoesNotExist


class BaseAdminHandler(BaseHandler):
    def if_admin(self):
        try:
            if not self.application.db.isUserAdmin(self.current_user):
                raise HTTPError(403)
        except DoesNotExist as e:
            raise HTTPError(403)