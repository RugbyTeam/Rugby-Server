from rugby import config

import tornado.websocket
import json
import os

class TailLogSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pass
    
    def on_message(self, message):
        data = json.loads(message)
        log_path = os.path.join(config.LOG_DIR, data['commit_id'])
        with open(log_path, 'r') as f:
            f.seek(data['size'])
            msg = {}
            msg['data'] = f.read()
            msg['size'] = f.tell()
            self.write_message(json.dumps(msg))

    def on_close(self):
        pass
