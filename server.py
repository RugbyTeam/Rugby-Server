from flask import Flask, request, json

app = Flask(__name__)

@app.route('/payload', methods=['POST'])
def github_payload():
    print "Printing events: "
    payload = request.get_json()
    events = payload['hook']['events']
    url = payload['repository']['clone_url']
    print url
    if 'push' in events:
        return "Received push"
    return "Received something..."

if __name__ == "__main__":
    app.run(debug=True)
