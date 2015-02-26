from rugby import config
import os
import tornado.websocket

class TailLogSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened"
    
    def on_message(self, message):
        build_msg = message.split(':')
        event = build_msg[0]
        commit_id = build_msg[1] 
        if event == "retrieve_logs":
            log_path = os.path.join(config.LOG_DIR, commit_id)
            self.write_message('Here is the log from ' + log_path)
            with open(log_path) as f:
                logs = f.read()
                self.write_message(logs)
    
    def on_close(self):
        print "WebSocket closed"
