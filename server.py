# internal
from github_repo import GithubRepo
import config

# external
from flask import Flask, request, json
from rugby import Rugby

# stdlib
import os

# Initializing necessary objects
app = Flask(__name__)
rugby = Rugby(config.RUGBY_ROOT)

"""
Routing Methods
"""
@app.route('/payload', methods=['POST'])
def github_payload():
    
    # We don't care about 'ping' events, we only care about 'push
    # events
    if request.headers.get('X-Github-Event') != 'push':
        return "Not a push event", 417
    
    payload = request.get_json()
    try:
        gh_repo = GithubRepo(payload)
    except Exception as e:
        return str(e), 200

    # We don't care about any other branch other than the 
    # 'default' branch
    if not gh_repo.cur_branch_is_default():
        return "Not default branch", 417
    
    # Copy over rugby conf from repo
    conf_dest_file = os.path.join(config.RUGBY_TMP, gh_repo.commit_id);
    try:
        conf_url = gh_repo.conf_url
        conf_data = requests.get(conf_url)
    except Exception as e:
        return "Failed to find .rugby.yml", 417
    
    with open(conf_dest_file, 'w') as f:
        f.write(conf_data.text())

    # Run Rugby
    Rugby.up(gh_repo.commit_id, conf_dest_file)

    return "Success", 200

@app.route('/')
def status():
    #TODO: Parse HTML status page here
    html = "This is a status page..."
    return html, 200

if __name__ == "__main__":
    app.run(debug=True)
