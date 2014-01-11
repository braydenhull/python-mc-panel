__author__ = 'brayden'

import json
from urllib2 import HTTPError
import urllib2
from tornado.httpclient import AsyncHTTPClient
import os
import pwd
import shutil
import subprocess


class Bukkit:
    def __init__(self, channel="rb", build=0):  # where 0 is latest
        # Channels are the build channels. valid ones as of now are: rb, beta, dev, next
        # more info at http://dl.bukkit.org/about/
        # Server flavours are: vanilla, bukkit
        self.ws = None
        self.args = None
        self.channel = channel
        self.build = build
        self.user_agent = 'python-mc-panel/0.1-dev'
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [{'User-Agent', self.user_agent}]
        self.client = AsyncHTTPClient()
        urllib2.install_opener(self.opener)

    class BukkitProvisionError(Exception):
        def __init__(self, message, name):
            self.message = message
            self.name = name

        def __str__(self):
            return repr(self.message)

    def _get_build_info(self, just_url=False):
        if not type(self.build) is int:
            raise self.BukkitProvisionError("Invalid build number", "InvalidBuildNumber")
        if self.build == 0:
            if just_url:
                return 'http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/view/latest/?_accept=application%2Fjson'
            else:
                request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/view/latest/?_accept=application%2Fjson')
        else:
            try:
                if just_url:
                    return 'http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/view/build-' + str(self.build) + '/?_accept=application%2Fjson'
                else:
                    request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/view/build-' + str(self.build) + '/?_accept=application%2Fjson')
            except HTTPError as e:
                if e.code == 404:
                    raise self.BukkitProvisionError("Build number not found.", "UnknownBuild")
                else:
                    raise self.BukkitProvisionError("Some HTTPError occurred: %s" % e, "UnknownHTTPError")
        result = json.loads(urllib2.urlopen(request).read())

        if result['is_broken']:
            raise self.BukkitProvisionError(result['broken_reason'], "BrokenBuild")

        return result

    def _get_builds(self, page=1, just_url=False):
        if not type(page) is int:
            raise TypeError
        if just_url:
            return 'http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/' +  self.channel + '/?_accept=application%2Fjson&page=' + str(page)
        else:
            request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/' +  self.channel + '/?_accept=application%2Fjson&page=' + str(page))
        result = urllib2.urlopen(request).read()
        result = json.loads(result)
        if result['results'] == 0:
            raise self.BukkitProvisionError("%s not recognised as a valid channel." % self.channel, "InvalidChannel Name")

        return result

    def get_download_url(self):
        details = self._get_build_info()
        return {'URL': 'http://dl.bukkit.org' + details['file']['url'], 'MD5': details['file']['checksum_md5'], 'Size': details['file']['size'], 'Filename': details['target_filename'], 'Downloads': details['download_count'], 'Created': details['created']}

    def install(self, ws, **kwargs):
        self.args = kwargs
        client = AsyncHTTPClient()
        self.ws = ws
        self.channel = self.args['stream']
        self.build = int(self.args['build'])

        self.home = self.ws.application.config.get('minecraft', 'home')
        if os.path.exists(self.home):
            os.system("useradd -m -s /bin/false -d %s/%s%s/ %s%s" % (self.home, self.ws.application.process_prefix, self.ws.server_id, self.ws.application.process_prefix, self.ws.server_id))
            self.ws.write_message({"success": True, "message": "Created new Linux user for server %s" % self.ws.server_id, "complete": False})
            self.home = pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_dir
            if not os.path.exists(self.home):
                os.mkdir(self.home)
                print type(self.ws.server_id)
                user = self.ws.application.process_prefix + str(self.ws.server_id)
                os.chown(self.home, pwd.getpwnam(user).pw_uid, pwd.getpwnam(user).pw_gid)

            with open(self.home + '/server.properties', 'w') as f:
                f.write("enable-query=true")  # enable the query API to get player listings

            os.chown(self.home + '/server.properties', pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_uid, pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_gid)
            os.chmod(self.home + '/server.properties', 0600)

            with open(os.path.dirname(self.ws.application.config.config_file) + '/bukkit_jar_cache/versions.json', 'r') as f:
                self.versions = json.load(f)

            if str(self.build) in self.versions['builds']:
                shutil.copyfile(self.versions['builds'][str(self.build)]['file'], self.home + '/minecraft.jar')
                self._finish_install()
            else:
                try:
                    self.ws.write_message({"message": "Starting Bukkit download.", "success": True, "complete": False})
                    client.fetch(self.get_download_url()['URL'], self._cb_download_handler, user_agent=self.user_agent, request_timeout=99999)  # if request_timeout isn't used, it'll die if it can't download fast enough
                except self.BukkitProvisionError as e:
                    self.ws.write_message({"message": "Encountered an error. %s: %s" % (e.name, e.message), "success": False, "complete": False})
        else:
            self.ws.write_message({"message": "Home directory is not present.", "success": False, "complete": False})

    def _cb_download_handler(self, response):
        if not response.error:
            self.ws.write_message({"message": "Completed download.", "success": True, "complete": False})

            with open(self.home + '/minecraft.jar', 'wb') as f:
                f.write(response.body)

            with open(os.path.dirname(self.ws.application.config.config_file) + '/bukkit_jar_cache/%s.jar' % self.build, 'wb') as f:
                    f.write(response.body)

            with open(os.path.dirname(self.ws.application.config.config_file) + '/bukkit_jar_cache/versions.json', 'w') as f:
                self.versions['builds'][str(self.build)] = {'file': os.path.dirname(self.ws.application.config.config_file) + '/bukkit_jar_cache/%s.jar' % str(self.build)}
                json.dump(self.versions, f)


            self._finish_install()  # Jump back into the install process
        else:
            self.ws.write_message({"message": "Download failed. %s: %s" % (response.code, response.error), "success": False, "complete": False})

    def update(self, handler, server_id, stream, autostart=False):
        self.channel = stream
        self.autostart = autostart
        self.build = 0  # latest
        self.home = '%s/%s%s/' % (handler.application.config.get('minecraft', 'home'), handler.application.process_prefix, server_id)
        try: handler.application.supervisor.stop_process(handler.application.process_prefix + server_id)
        except Exception as e: print e
        os.remove(self.home + '/minecraft.jar')
        self.build_info = self._get_build_info()
        with open(os.path.dirname(handler.application.config.config_file) + '/bukkit_jar_cache/versions.json', 'r') as f:
            self.versions = json.load(f)
        if not str(self.build_info['build_number']) in self.versions['builds']:
            request = urllib2.urlopen('http://dl.bukkit.org' + self.build_info['file']['url'])
            with open(self.home + '/minecraft.jar', 'wb') as f:
                shutil.copyfileobj(request, f)
        else:
            shutil.copyfile(self.versions['builds'][str(self.build_info['build_number'])]['file'], self.home + '/minecraft.jar')
        if self.autostart:
            handler.application.supervisor.start_process(handler.application.process_prefix + server_id)

        return True

    def _finish_install(self):
        os.chown(self.home + '/minecraft.jar', pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_uid, pwd.getpwnam(self.ws.application.process_prefix + str(self.ws.server_id)).pw_gid)
        os.chmod(self.home + '/minecraft.jar', 0700)
        self.ws.application.supervisor.write_program_config(self.ws.application.process_prefix + str(self.ws.server_id), os.path.dirname(self.ws.application.supervisor_config_path), self.args['memory'], self.ws.application.process_prefix + str(self.ws.server_id), self.home + '/minecraft.jar', additional_jar_options="--nojline --server-ip %s --server-port %s" % (self.args['address'], self.args['port']))
        self.ws.write_message({"success": True, "message": "Created supervisor config", "complete": False})
        self.ws.write_message({"success": True, "message": "Starting server!", "complete": True})

    def get_streams(self, handler):
        handler.finish({"result": {"results": {"values": [{"value": "rb", "name": "Recommended"},
                                                          {"value": "dev", "name": "Development"},
                                                          {"value": "beta", "name": "Beta"}]},
                                   "success": True,
                                   "message": None}})

    def get_builds(self, handler):
        self.handler = handler
        self.client.fetch(self._get_builds(just_url=True), self.get_builds_http_handler, user_agent=self.user_agent)

    def get_builds_http_handler(self, response):
        response = json.loads(response.body)['results']
        builds = []
        for build in response:
            if not build['is_broken']:  # exclude broken builds, there's only one in the rb list right now though but dev probably has some
                builds.append(build['build_number'])
                self.handler.application.craftbukkit_build_list[build['build_number']] = build['version']
        self.handler.finish({'result': {
            'message': None,
            'results': {'builds': builds, 'latest_version': response[0]['version']},
            'success': True
        }})

    def get_build_info(self, handler):
        self.handler = handler
        if not self.build in self.handler.application.craftbukkit_build_list:
            self.client.fetch(self._get_build_info(just_url=True), self.get_build_info_http_handler, user_agent=self.user_agent)
        else:
            self.handler.finish({"result": {"results": {"info": {"version": self.handler.application.craftbukkit_build_list[self.build]}},
                                            "success": True,
                                            "message": None,
                                            "cached": True}})

    def get_build_info_http_handler(self, response):
        build_info = json.loads(response.body)
        self.handler.application.craftbukkit_build_list[self.build] = build_info['version']
        self.handler.finish({"result": {"results": {"info": {"version": build_info['version']}},
                                        "success": True,
                                        "message": None,
                                        "cached": False}})

    def delete_server(self, server_id, application):
        try:
            try:
                application.supervisor.server.supervisor.stopProcess(application.process_prefix + server_id)
            except:
                pass
            os.remove(os.path.dirname(application.supervisor_config_path) + '/conf.d/%s%s.conf' % (application.process_prefix, server_id))
        except OSError as e:
            print "Failed to remove supervisord config for server %s. Error %s" % (server_id, e)

        try:
            application.supervisor.server.supervisor.clearProcessLogs(application.process_prefix + server_id)
        except Exception as e:
            print "Failed to remove process logs for server %s. Error: %s" % (server_id, e)

        try:
            with open('/var/log/minecraft/%s%s.log' % (application.process_prefix, server_id), 'w') as f:
                f.write('')  # clear log
        except IOError as e:
            print "Failed to blank out log for server %s. Error %s" % (server_id, e)

        try:
            application.supervisor.server.supervisor.removeProcessGroup(application.process_prefix + server_id)
        except Exception as e:
            print "Failed to remove process group from supervisord for sever %s. Error: %s." % (server_id, e)

        try:
            application.supervisor.server.supervisor.reloadConfig()
        except Exception as e:
            print "Failed to reload config for supervisord from server %s. Error: %s" % (server_id, e)

        try:
            shutil.rmtree(application.config.get('minecraft', 'home') + '/%s%s/' % (application.process_prefix, server_id))
        except OSError as e:
            print "Failed to remove home directory for server %s. Error: %s" % (server_id, e)

        try:
            subprocess.Popen(['userdel', '%s%s' % (application.process_prefix, server_id)], shell=False)
        except OSError as e:
            print "Failed to remove Linux user for server %s. Error: %s" % (server_id, e)

        return True