from rugby import config

from ansi2html import Ansi2HTMLConverter

from datetime import datetime
from dateutil.tz import tzlocal, gettz
import dateutil.parser

import tornado.websocket
import codecs
import json
import os

def state_to_display_status(state):
    display_status = None
    if state == 'RugbyState.SUCCESS':
        display_status = 'passed'
    elif state == 'RugbyState.ERROR':
        display_status = 'failed'
    else:
        display_status = 'running'
    return display_status;

class TailLogSocketHandler(tornado.websocket.WebSocketHandler):

    # Static reference to rugby for commit data
    rugby = None;

    def open(self):
        pass
    
    def on_message(self, message):
        data = json.loads(message)
        log_path = os.path.join(config.LOG_DIR, data['commit_id'])
        
        build_info = TailLogSocketHandler.rugby.get_info(data['commit_id'])
        display_status = state_to_display_status(build_info['state'])
        commit_date = dateutil.parser.parse(build_info['commit_timestamp'])
        td = datetime.now(tzlocal()) - commit_date
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60

        with codecs.open(log_path, 'r', 'utf-8') as f:
            f.seek(data['size'])
            html = self._convert_log_to_html(f.read())
            msg = {}
            msg['data'] = html
            msg['size'] = f.tell()
            msg['display_status'] = display_status
            msg['commit_url'] = build_info['commit_url']
            msg['commit_time'] = {
                'days': days,
                'hours': hours,
                'minutes':  minutes
            }
            self.write_message(json.dumps(msg))

    def on_close(self):
        pass

    def _convert_log_to_html(self, log_string):
        def strip_enclosing_html(html):
            ret = html.split('<pre id="content">')[1]
            ret = ret.split('</pre>')[0]
            ret = ret.rstrip()
            return ret

        conv = Ansi2HTMLConverter(inline=True)
        html = unicode(conv.convert(log_string))
        return strip_enclosing_html(html)

