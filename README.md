# Rugby-Server
Web server for Rugby

Instructions:
Download ngrok at https://ngrok.com/download

```
ngrok 5000
```

Take note of the *.ngrok.com URL in the line:

```
Forwarding http://459ab83b.ngrok.com -> 127.0.0.1:5000
```

Download pip at https://pip.pypa.io/en/latest/installing.html

```
pip install Flask
python server.py
```

Go to Rugby-Playbooks at https://github.com/RugbyTeam/Rugby-Playbooks
Go to settings -> webhooks
Add a new webhook with your ngrok URL above.

