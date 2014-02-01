__author__ = 'brayden'

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner
import unittest
import requests
import websocket
import json
import time


class TestWebPanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = 'localhost'
        cls.default_username = 'Admin'
        cls.default_password = 'admin'
        request = requests.post('http://%s/ajax/performLogin' % cls.host, params={"username": cls.default_username, "password": cls.default_password, "expires": 99})
        if request.json()['result']['success']:
            cls.cookies = dict(session=request.json()['result']['cookie'])
        else:
            raise unittest.SkipTest("Could not authenticate with panel") # thanks to http://stackoverflow.com/a/11453318/2077881

    def test_aHomePage(self):
        r = requests.get('http://%s/' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "Home page did not return status 200 OK, instead returned: " + str(r.status_code))

    def test_bServersIndex(self):
        r = requests.get('http://%s/servers/' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "Servers Page did not return status 200 OK, instead returned: " + str(r.status_code))

    def test_cServersGetBuilds(self):
        r = requests.post('http://%s/servers/ajax/getInfo' % self.host, cookies=self.cookies, params={"server_type": "craftbukkit", "request_type": "get_builds", "stream": "rb"})
        self.assertEquals(r.json()['result']['success'], True, "get_builds was not successful, message: " + str(r.json()['result']['message']))

    def test_dServersCheckValidAddress(self):
        r = requests.post('http://%s/servers/ajax/checkAddress' % self.host, cookies=self.cookies, params={"address": "0.0.0.0", "port": 25565})
        self.assertEquals(r.json()['result']['success'], True, "checkAddress which should've worked was not successful")

    def test_eServersCheckInvalidAddress(self):
        r = requests.post('http://%s/servers/ajax/checkAddress' % self.host, cookies=self.cookies, params={"address": "0.0.0.0", "port": 99999})
        self.assertEqual(r.json()['result']['success'], False, "checkAddress was a success for invalid address")

    def test_fServersGetBuildInfo(self):
        r = requests.post('http://%s/servers/ajax/getInfo' % self.host, cookies=self.cookies, params={"server_type": "craftbukkit", "request_type": "get_build_info", "build": 2918})
        self.assertEqual(r.json()['result']['success'], True, "get_build_info was not successful, returned: " + str(r.json()['result']['message']))

    def test_gCreateServerWebsocket(self):
        ws = websocket.create_connection("ws://%s/servers/websocket/createServer" % self.host)
        ws.send(json.dumps({"params": {"memory": 512, "address": "0.0.0.0", "port": 25565, "build": 2918, "stream": "rb", "type": "craftbukkit"}, "authentication": self.cookies['session'], "owner": self.default_username}))
        while True:
            result = ws.recv()
            if json.loads(result)['complete']:
                break
            elif not json.loads(result)['success']:
                self.fail("websocket create returned error, message: " + str(json.loads(result)['message']))

        time.sleep(30) # wait for server to finish starting up, just so that the files are present for getplayers etc. are tested

    def test_hServerCheckDashboard(self):
        r = requests.get('http://%s/servers/1/' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "Server dashboard did not return status 200 OK, instead returned: " + str(r.status_code))

    def test_iServerGetProcessInfo(self):
        r = requests.post('http://%s/servers/1/ajax/getProcessInfo' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getProcessInfo was not successful, returned: " + str(r.json()['result']['message']))

    def test_jServerCheckPlayers(self):
        r = requests.get('http://%s/servers/1/players' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "players page did not return status 200 OK, instead returned: " + str(r.status_code))

    def test_kServerGetPlayers(self):
        r = requests.post('http://%s/servers/1/ajax/getPlayers' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getPlayers was not successful, returned: " + str(r.json()['result']['message']))

    def test_lServerGetOps(self):
        r = requests.post('http://%s/servers/1/ajax/getOperators' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getOperators was not successful, returned: " + str(r.json()['result']['message']))

    def test_mServerGetBannedPlayers(self):
        r = requests.post('http://%s/servers/1/ajax/getBannedPlayers' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getBannedPlayers was not successful, returned: " + str(r.json()['result']['message']))

    def test_nServerBanPlayer(self):
        r = requests.post('http://%s/servers/1/ajax/banPlayer' % self.host, cookies=self.cookies, params={"player": "test"})
        self.assertEqual(r.json()['result']['success'], True, "banPlayer was not successful, returned: " + str(r.json()['result']['message']))
        time.sleep(0.50) # Give the I/O enough time to catch up for the next request, this seems sufficient for HDDs and SSDs
        r = requests.post('http://%s/servers/1/ajax/getBannedPlayers' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getBannedPlayers was not successful, returned: " + str(r.json()['result']['message']))
        self.assertTrue('test' in r.json()['result']['results']['players'], "Banned player was not found in getBannedPlayers")

    def test_oServerOpPlayer(self):
        r = requests.post('http://%s/servers/1/ajax/opPlayer' % self.host, cookies=self.cookies, params={"player": "test"})
        self.assertEqual(r.json()['result']['success'], True, "opPlayer was not successful, returned: " + str(r.json()['result']['message']))
        time.sleep(0.50) # same as above with server ban player
        r = requests.post('http://%s/servers/1/ajax/getOperators' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getOperators was not successful, returned: " + str(r.json()['result']['message']))
        self.assertTrue('test' in r.json()['result']['ops'], "Could not find operator in getOperators: " + str(r.json()))

    def test_pServerGetLog(self):
        r = requests.post('http://%s/servers/1/ajax/getLog' % self.host, cookies=self.cookies, params={"lines": 100})
        self.assertEqual(r.json()['result']['success'], True, "getLog was not successful, returned: " + str(r.json()['result']['message']))

    def test_qServerProperties(self):
        r = requests.get('http://%s/servers/1/properties' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "Server properties did not return 200 OK, instead returned: " + str(r.status_code))

    def test_rServerUpdatePage(self):
        r = requests.get('http://%s/servers/1/update' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "Server update page did not return 200 OK, instead returned: " + str(r.status_code))

    def test_sAdminUsers(self):
        r = requests.get('http://%s/admin/users' % self.host, cookies=self.cookies)
        self.assertEqual(r.status_code, 200, "Admin users page did not return 200 OK, instead returned: " + str(r.status_code))

    def test_tAdminGetUsers(self):
        r = requests.post('http://%s/admin/ajax/getUsers' % self.host, cookies=self.cookies)
        self.assertEqual(r.json()['result']['success'], True, "getUsers was not successful, returned: " + str(r.json()['result']['message']))

    def test_uAdminAddUser(self):
        r = requests.post('http://%s/admin/ajax/addUser' % self.host, cookies=self.cookies, params={"username": "test", "password": "test", "is_admin": "false"})
        self.assertEqual(r.json()['result']['success'], True, "Admin addUser was not successful, returned: " + str(r.json()['result']['message']))

    def test_vAdminDeleteUser(self):
        r = requests.post('http://%s/admin/ajax/deleteUser' % self.host, cookies=self.cookies, params={"user": "test"})
        self.assertEqual(r.json()['result']['success'], True, "Admin deleteUser was not successful, returned: " + str(r.json()['result']['message']))

    def test_wServersStopServerNoForce(self):
        r = requests.post('http://%s/servers/ajax/stopServer' % self.host, cookies=self.cookies, params={"server_id": 1, "force": "false"})
        time.sleep(5) # wait for server to stop for next test, starting it
        self.assertEqual(r.json()['result']['success'], True, "Servers stop server no force was not successful, returned: " + str(r.json()['result']['message']))

    def test_xServersStartServer(self):
        r = requests.post('http://%s/servers/ajax/startServer' % self.host, cookies=self.cookies, params={"server_id": 1})
        time.sleep(1) # wait for process to start, for force stop it edoesn't need to actually fully start, just have a PID that supervisord can see
        self.assertEqual(r.json()['result']['success'], True, "Servers start server was not successful, returned: " + str(r.json()['result']['message']))

    def test_yServersStopServerWithForce(self):
        r = requests.post('http://%s/servers/ajax/stopServer' % self.host, cookies=self.cookies, params={"server_id": 1, "force": "true"})
        self.assertEqual(r.json()['result']['success'], True, "Servers stop server with force was not successful, returned: " + str(r.json()['result']['message']))

    def test_zServersDeleteServer(self):
        r = requests.post('http://%s/servers/ajax/deleteServer' % self.host, cookies=self.cookies, params={"server_id": 1})
        self.assertEqual(r.json()['result']['success'], True, "Servers delete server was not successful, returned: " + str(r.json()['result']['message']))

if __name__ == '__main__':
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner, verbosity=3)