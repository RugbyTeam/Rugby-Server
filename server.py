from flask import Flask, request, json
from rugby import Rugby
from rugby import Parser
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
    url = payload['repository']['clone_url']
    dirname = payload['commits'][-1]['id'] 
    os.mkdir(dirname)
    yml_file = urllib.URLopener()
    url = base_url+payload['repository']['full_name']+yml
    print url
    yml_file.retrieve(url, dirname + "/rugby.yaml")
    print dirname
    path_to_yml = dirname + "/rugby.yaml"
    ##----not sure were to put this, Parsing##
    p = Parser(path_to_yml)
    print p.parsed_yml 
    
    ##---------
    if request.headers.get('X-Github-Event') == 'push':
        return "Received push"
    return "Received something..."

@app.route('/')
def status():
    #TODO: Parse HTML status page here
    html = "This is a status page..."
    commit_id = "genericcommitID"
    clone_url = "this/is/a/url"
    rugby.up(commit_id, clone_url)
    return html

if __name__ == "__main__":
    app.run(debug=True)
