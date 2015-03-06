import os

# Web server constants
RAW_GIT_URL_BASE = 'https://raw.githubusercontent.com'
RUGBY_ROOT = '/opt/Rugby'
RUGBY_CONF = '.rugby.yml'
RUGBY_TMP = '/tmp'
STATICS_DIR = '/static'

# Get environment variables for mail server
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWD = os.getenv('GMAIL_PASSWD')

# Where the template files are located
TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
EMAIL_TEMPLATE_FILE = os.path.join(TEMPLATES_DIR, 'email_template.j2')
