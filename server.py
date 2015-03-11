# internal
from github_repo import GithubRepo
from log_socket import TailLogSocketHandler
import config

# external
from rugby import Rugby
from mail_server import MailServer
from datetime import datetime
from dateutil.tz import tzlocal
import dateutil.parser
import tornado.web
import tornado.escape
import tornado.gen
import tornado.httpclient
import tornado.websocket
import jinja2

# stdlib
import os

#Where email template is located
email_template_file = config.EMAIL_TEMPLATE_FILE

# Dumb class (to avoid some code rewrites...)
# Should probably move this representation to Rugby side... but it's fine since it's server only
class Commit:
    def __init__(self, commit_obj):
        self.commit_message = commit_obj['commit_message']
        self.commit_id = commit_obj['commit_id']
        state = commit_obj['state']
        self.commit_url = commit_obj['commit_url']

        commit_date = dateutil.parser.parse(commit_obj['commit_timestamp'])
        td = datetime.now(tzlocal()) - commit_date
        self.days, self.hours, self.minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
        self.total_seconds = int(td.total_seconds())
        
        self.time_label = None
        if self.days > 0:
            self.time_label = '%d days ago' % self.days
        elif self.hours > 0:
            self.time_label = '$d hours ago' % self.hours
        else:
            self.time_label = '%d minutes ago' % self.minutes

        if state == 'RugbyState.SUCCESS':
            self.display_status = 'passed'
        elif state == 'RugbyState.ERROR':
            self.display_status = 'failed'
        else:
            self.display_status = 'running'

# Initializing necessary objects
rugby = Rugby(config.RUGBY_ROOT)

# Set TailLogSocket reference
TailLogSocketHandler.rugby = rugby

def print_callback(commit_id, state):
    print "ID: {} \nState: {}\n".format(commit_id, state)

def render_email(commit_info):
    """ 
    Renders the body of an email in HTML using jinja2 templating.
    """
    with open(email_template_file) as template_file:
        j2_template = jinja2.Template(template_file.read())
        return j2_template.render(commit_id=commit_info['commit_id'],
                                  commit_url=commit_info['commit_url'],
                                  author_login=commit_info['author_login'], 
                                  author_avatar_url=commit_info['author_avatar_url'])


def email_callback(commit_id, state):
    # Commit_info contains all information from the given commit_id 
    commit_info = rugby.get_info(commit_id)
    recipients = commit_info['contributors_email']

    subject = "The build broke!"
    if state == 'RugbyState.ERROR':
        ms = MailServer()
        body = render_email(commit_info)
        ms.send(recipients, subject, body)

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
            raise
            return

        # We don't care about any other branch other than the 'default' branch
        if not gh_repo.cur_branch_is_default():
            message = 'Not a default branch.'
            self.send_error(417, message=message)
            return
        print "Trying to fetch"
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
        rugby.start_runner(gh_repo.get_build_info(), config_dest_file, print_callback, email_callback)

        # Start logging task
        self.write('Success')

class StatusPageHandler(tornado.web.RequestHandler):
    def get(self):
        builds = [Commit(x) for x in rugby.get_builds()]
        builds = sorted(builds, key=lambda commit: commit.total_seconds)
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
