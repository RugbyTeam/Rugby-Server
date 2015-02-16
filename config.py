import os

# Web server constants
RAW_GIT_URL_BASE = 'https://raw.githubusercontent.com'
RUGBY_ROOT = '/opt/Rugby'
RUGBY_CONF = '.rugby.yml'
RUGBY_TMP = '/tmp'

# Get environment variables for mail server
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWD = os.getenv('GMAIL_PASSWD')
