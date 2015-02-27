# internal
from github_repo import GithubRepo
from log_socket import TailLogSocketHandler
import config

# external
from rugby import Rugby
import tornado.web
import tornado.escape
import tornado.gen
import tornado.httpclient
import tornado.websocket

# stdlib
import os
class Commit:
    def __init__(self, msg, cid, status):
        self.commit_message = msg
        self.commit_id = cid
        self.display_status = status

commit1 = Commit('Manny broke everything',
                 '55555',
                 'failed')
commit2 = Commit('Fixed all of the project',
                 '22222',
                 'running')
 
commit3 = Commit('Deleted all the tests',
                 '33333',
                 'passed')

builds = [commit1, commit2, commit3]

# Initializing necessary objects
rugby = Rugby(config.RUGBY_ROOT)

class GitHubHookHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.github_event = self.request.headers.get('X-Github-Event')
        if self.request.body:
            try:
                self.payload = tornado.escape.json_decode(self.request.body)
            except ValueError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message)
                return

    @tornado.gen.coroutine
    def post(self):
        # We don't care about 'ping' events, we only care about 'push' events
        http_client = tornado.httpclient.AsyncHTTPClient()

        if self.github_event != 'push':
            self.send_error(417, message="Not a push event.")
            return
        try:
            gh_repo = GithubRepo(self.payload)
        except Exception as e:
            self.write(str(e))
            self.finish()
            return
        # We don't care about any other branch other than the 'default' branch
        if not gh_repo.cur_branch_is_default():
            message = 'Not a default branch.'
            self.send_error(417, message=message)
            return

        # Copy over rugby conf from repo
        config_dest_file = os.path.join(config.RUGBY_TMP, gh_repo.commit_id);
        try:
            config_url = gh_repo.config_url
            config_data = yield http_client.fetch(config_url)
        except Exception as e:
            message = 'Failed to find .rugby.yml.' + str(e)
            self.send_error(417, message=message)
            return

        with open(config_dest_file, 'w') as f:
            f.write(config_data.body)

        # Run Rugby
        Rugby.up(gh_repo.commit_id, config_dest_file)

        # Start logging task
        self.write('Success')



class StatusPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.getcwd() + '/static/index.html', title="Rugby", builds=builds)

class BuildPageHandler(tornado.web.RequestHandler):
    def get(self, commit_id):
        for commit in builds:
            if commit.commit_id == commit_id:
                self.render(os.getcwd() + '/static/build_page.html', title="Build", commit_id=commit_id, build=commit)
                break
        else:
            self.write('Page Not Found')

if __name__ == "__main__":
    github_hook_route = tornado.web.url(r'/payload', GitHubHookHandler)
    sha1_regex = r'/([0-9a-f]{5,40})?'
    status_page_route = tornado.web.url(r'/', StatusPageHandler)
    web_socket_route = tornado.web.url(r'/websocket', TailLogSocketHandler)
    build_page_route = tornado.web.url(r'/build' + sha1_regex, BuildPageHandler)

    routes = [github_hook_route, status_page_route, web_socket_route, build_page_route]

    settings = {
        "static_path":  os.getcwd() + '/static',
    }

    app = tornado.web.Application(routes, **settings)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
