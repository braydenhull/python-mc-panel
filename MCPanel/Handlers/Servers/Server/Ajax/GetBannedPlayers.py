__author__ = 'brayden'

from tornado.web import asynchronous
from tornado.web import authenticated
from Base import BaseServerAjaxHandler


class GetBannedPlayersHandler(BaseServerAjaxHandler):
    @asynchronous
    @authenticated
    def post(self, server_id):
        with open(self.application.config.get('minecraft', 'home') + '/%s%s/banned-players.txt' % (self.application.process_prefix, server_id), 'r') as f:
            lines = list(line for line in (l.strip() for l in f) if line) # this mess provided by http://stackoverflow.com/a/4842095/2077881

        result = {"players": [], "details": {}}

        for line in lines:
            if line.startswith('#'):
                continue

            player = line.split('|')
            result['players'].append(player[0])

            if len(player) > 1:  # back in my day banned-players.txt was just a list of names
                result['details'][player[0]] = {
                    "Ban Date": player[1],
                    "Banned By": player[2],
                    "Banned Until": player[3],
                    "Reason": player[4]
                }
            else:
                result['details'][player[0]] = {
                    "Ban Date": "Not Available",
                    "Banned By": "Unknown",
                    "Banned Until": "Forever",
                    "Reason": "Unknown"
                }

        self.finish({"result": {"success": True, "message": None, "results": result}})