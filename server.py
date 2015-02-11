from flask import Flask, request, json
from Rugby import Rugby
import urllib
import os

rugby = Rugby()
app = Flask(__name__)
#this is the url that is used to download the rugby.yml file
baseurl = "https://raw.githubusercontent.com/"
yml = "/master/.rugby.yml"
@app.route('/payload', methods=['POST'])
def github_payload():
    payload = request.get_json()
    url = payload['repository']['clone_url']
    dirname = payload['commits'][-1]['id'] 
    os.mkdir(dirname)
    ymlfile = urllib.URLopener()
    url = baseurl+payload['repository']['full_name']+yml
    print url
    ymlfile.retrieve(url, dirname + "/rugby.yaml")
    print dirname
    if request.headers.get('X-Github-Event') == 'push':
        return "Received push"
    return "Received something..."

if __name__ == "__main__":
    rugby.init("/Users/yuki/TEST")
    rugby.up()
    app.run(debug=True)
