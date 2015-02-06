from flask import Flask, request
app = Flask(__name__)

@app.route('/payload', methods=['POST'])
def github_payload():
    print request.data
    return "Received"

if __name__ == "__main__":
    app.run()
