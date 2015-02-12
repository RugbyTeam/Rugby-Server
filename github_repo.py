# internal
import config

# stdlib
import json
import os
import urllib2

class RepoError(Exception):
    pass

class GithubRepo:
    def __init__(self, payload):
        """
            _payload = dict payload from a web githook
            commit_id = commit sha1 hash
            clone_url = URL used for cloning this repo
            cur_branch = current branch repo is on
            default_branch = default repo branch
            config_url = path to raw rugby config file on github
            contrib_list = list of dict, each containing a contributor's login and email
                [{'login':'username', 'email':'email@email.com'}]
        """
        self._payload = payload
        self.commit_id = payload['head_commit']['id']
        self.clone_url = payload['repository']['clone_url']
        self.cur_branch = payload['ref'].split('/')[-1]
        self.default_branch = payload['repository']['default_branch']
        self.config_url = self._build_config_url()
        self.contrib_list = self._fetch_all_contributors()

    def cur_branch_is_default(self):
        """
        Returns true if the current branch is also
        the default branch for the repository
        """
        return self.cur_branch == self.default_branch

    def _build_config_url(self):
        """
        Helper function to build the raw url to a rugby
        conf
        """
        raw_base = config.RAW_GIT_URL_BASE
        conf_name = config.RUGBY_CONF
        repo_name = self._payload['repository']['full_name']
        raw_git_url =  os.path.join(raw_base, repo_name, self.default_branch, conf_name)
        return raw_git_url

    def _fetch_all_contributors(self):
        """
        Helper function to extract all contributors
        email addresses

        Returns an array of objects
            [{ "login" : "omoman", "email" : "email@gmail.com"}]
        """
        contrib_url = self._payload['repository']['contributors_url']
        contrib_req = urllib2.Request(contrib_url)
        try:
            contrib_data = urllib2.urlopen(contrib_req).read()
        except ValueError:
            raise RepoError("Failed to fetch contributor data")

        # Convert contrib_data json string to dict
        contrib_data = json.loads(contrib_data)
        
        contrib_info = []
        for contrib in contrib_data:
            # Fetch contributors profile
            profile_url = contrib['url']
            profile_req = urllib2.Request(profile_url)
            try:
                profile_data = urllib2.urlopen(profile_req).read()
            except ValueError:
                raise RepoError("Failed to fetch user data")

            # Convert profile_data json string to dict
            profile_data = json.loads(profile_data)
            
            contrib_info.append({'login' : profile_data['login'], 'email' : profile_data['email']})
        
        return contrib_info


