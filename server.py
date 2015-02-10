from flask import Flask, request, json
from Rugby import Rugby

rugby = Rugby()
app = Flask(__name__)

@app.route('/payload', methods=['POST'])
def github_payload():
    payload = request.get_json()
    url = payload['repository']['clone_url']
    print url

    if request.headers.get('X-Github-Event') == 'push':
        return "Received push"
    return "Received something..."

if __name__ == "__main__":
    rugby.init("/Users/yuki/TEST")
    rugby.up()
    app.run(debug=True)
