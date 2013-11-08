__author__ = 'brayden'

import xmlrpclib
import ConfigParser
import os


class Supervisor:
    def __init__(self, username, password):
        self.server = xmlrpclib.Server('http://%s:%s@127.0.0.1:9001/RPC2' % (username, password))

    def is_process_running(self, server_id):
        state = self.server.supervisor.getProcessInfo(server_id)['statename']
        if state == "RUNNING":
            return True
        else:
            return False

    def run_command(self, server_id, command):
        return self.server.supervisor.sendProcessStdin(server_id, command)

    def get_pid(self, server_id):
        return self.server.supervisor.getProcessInfo(server_id)['pid']

    def start_process(self, server_id):
        return self.server.supervisor.startProcess(server_id)

    def write_program_config(self, process_name, directory, memory, username, jar_file_location, additional_options='', additional_jar_options=''):
        config = ConfigParser.RawConfigParser()
        filename = directory + '/conf.d/%s.conf' % process_name
        if not os.path.exists(filename):
            with file(filename, 'a'):
                os.utime(filename, None) # touch the file

        config.read(filename)
        section_name = 'program:%s' % process_name # just make it easy to change later!
        config.add_section(section_name)
        config.set(section_name, 'command', "bash -c 'java -Xmx${MEM}M $ADDITIONAL_OPTS -jar $JAR_FILE $ADDITIONAL_JAR_OPTS'")
        environment = 'MEM="%s", JAR_FILE="%s", ADDITIONAL_OPTS="%s", ADDITIONAL_JAR_OPTS="%s"' % (memory, jar_file_location, additional_options, additional_jar_options)
        config.set(section_name, 'environment', environment)
        config.set(section_name, 'directory', os.path.dirname(jar_file_location)) # cwd
        config.set(section_name, 'autorestart', False) # will try to autorestart when "stop" is used on server otherwise
        config.set(section_name, 'user', username)
        config.set(section_name, 'stdout_logfile', '/var/log/minecraft/%s.log' % process_name)
        config.set(section_name, 'stderr_logfile', '/var/log/minecraft/%s.log' % process_name)
        with open(filename, 'w') as f:
            config.write(f)
        self.server.supervisor.reloadConfig() # undocumented feature :(
        self.server.supervisor.addProcessGroup(process_name) # also undocumented quirk which will auto start the server!