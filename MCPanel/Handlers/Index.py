__author__ = 'brayden'

from tornado.web import asynchronous
from Base import BaseHandler
from tornado.web import authenticated
import tornado.httpclient
import tempfile
import os


class IndexHandler(BaseHandler):
    @asynchronous
    @authenticated
    def get(self):
        #self.application.acl([], self.current_user, 1)
        #self.HttpDownload("http://dl.bukkit.org/latest-rb/craftbukkit.jar")
        self.render(self.application.settings['template_path'] + '/index.template', pageName="Home")

    class HttpDownload(object):
        def __init__(self, url):
            self.tempfile = tempfile.NamedTemporaryFile(delete=False)
            req = tornado.httpclient.HTTPRequest(
                url = url,
                streaming_callback=self.streaming_callback,
                request_timeout=999999 # needs to be very long else it'll timeout due to size of file it is downloading
            )
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(req, self.async_callback)

        def streaming_callback(self, data):
            self.tempfile.write(data)
            print len(data)

        def async_callback(self, response):
            self.tempfile.flush()
            self.tempfile.close()
            if response.error:
                print "Download failed."
                os.unlink(self.tempfile.name)
            else:
                print "Great success! %s" % self.tempfile.name