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

# Dumb class (to avoid some code rewrites...)
# Should probably move this representation to Rugby side... but it's fine since it's server only
class Commit:
    def __init__(self, commit_obj):
        self.commit_message = commit_obj['commit_message']
        self.commit_id = commit_obj['commit_id']
        state = commit_obj['state']
        if state == 'RugbyState.SUCCESS':
            self.display_status = 'passed'
        elif state == 'RugbyState.ERROR':
            self.display_status = 'failed'
        else:
            self.display_status = 'running'

# Initializing necessary objects
rugby = Rugby(config.RUGBY_ROOT)

def print_callback(commit_id, state):
    print "ID: {} \nState: {}\n".format(commit_id, state)

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
        rugby.start_runner(gh_repo.commit_id, gh_repo.commit_message,
                           gh_repo.clone_url, gh_repo.raw_url, config_dest_file, print_callback)

        # Start logging task
        self.write('Success')

class StatusPageHandler(tornado.web.RequestHandler):
    def get(self):
        builds = [Commit(x) for x in rugby.get_builds()]
        self.render(os.getcwd() + '/static/index.html', title="Rugby", builds=builds)

class BuildPageHandler(tornado.web.RequestHandler):
    def get(self, commit_id):
        builds = rugby.get_builds()
        for build in builds:
            commit = Commit(build)
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

    # Routing settings for static files
    settings = {
        "static_path":  os.getcwd() + '/static',
    }

    app = tornado.web.Application(routes, **settings)
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
