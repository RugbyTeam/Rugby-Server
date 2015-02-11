from flask import Flask, request, json
from rugby import Rugby
from rugby import Parser
import urllib
import os

rugby = Rugby()
app = Flask(__name__)
#this is the url that is used to download the rugby.yml file
base_url = "https://raw.githubusercontent.com/"
yml = "/master/.rugby.yml"
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

if __name__ == "__main__":
    rugby.init("/Users/yuki/TEST")
    rugby.up()
    app.run(debug=True)
