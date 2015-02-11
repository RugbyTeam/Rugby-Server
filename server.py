from flask import Flask, request, json
from rugby import Rugby
import urllib
import os

# Initializing necessary objects
app = Flask(__name__)
rugby = Rugby(os.getcwd())

#this is the url that is used to download the rugby.yml file
base_url = "https://raw.githubusercontent.com/"
yml = "/master/.rugby.yml"

"""
Routing Methods

"""
@app.route('/payload', methods=['POST'])
def github_payload():
    payload = request.get_json()
    commit_id = payload['commits'][-1]['id']
    clone_url = payload['repository']['clone_url']
    config_url = base_url + payload['repository']['full_name'] + yml
    config_file = "/tmp/"+commit_id
    # We grab the .rugby.yml file from the repo and pass it to Rugby object
    try:
        yml_file = urllib.URLopener()
        yml_file.retrieve(config_url, config_file)
    except URLError:
        print "Rugby-Server URLError on config retrieval"
        return "Config Retrieval Error", 500

    if request.headers.get('X-Github-Event') == 'push':
        rugby.up(commit_id, config_file)

    return "Received something...", 200

@app.route('/')
def status():
    #TODO: Parse HTML status page here
    html = "This is a status page..."
    return html, 200

if __name__ == "__main__":
    app.run(debug=True)
