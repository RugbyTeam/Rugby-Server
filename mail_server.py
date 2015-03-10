# internal
import config

# stdlib
import threading

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_SERVER_HOST = 'smtp.gmail.com'
GMAIL_SERVER_PORT = 465

class MailServer():
    def __init__(self, **kwargs):
        """
        Sets up which smtp server to use and also
        provide mail credentials

        By default for the mail server, we use gmail.

        Also by default, uses the GMAIL_USER and GMAIL_PASSWD
        environment variables as the mail credentials
        """
        if 'host' not in kwargs:
            self.host = GMAIL_SERVER_HOST
        else:
            self.host = kwargs['host']

        if 'port' not in kwargs:
            self.port = GMAIL_SERVER_PORT
        else:
            self.port = kwargs['port']

        if 'sender' not in kwargs:
            self.sender = config.GMAIL_USER
        else:
            self.sender = kwargs['sender']

        if 'send_passwd' not in kwargs:
            self.sender_passwd = config.GMAIL_PASSWD
        else:
            self.sender_passwd = kwargs['sender_passwd']

    def send(self, recipients, subject, body):
        """
        Calls the private _send function in a new thread
        Note: should probably start a new process than spawn another thread
        """
        t = threading.Thread(target=self._send, args=(recipients, subject, body))
        t.start()

    def _send(self, recipients, subject, body):
        """
        """
        if isinstance(recipients, type(list)):
          to = ", ".join(recipients)
        else:
            to = recipients

        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        mail_server = self._setup_mail_server()
        mail_server.sendmail(self.sender, to, msg.as_string())
        mail_server.close()

    def _setup_mail_server(self):
        mail_server = smtplib.SMTP_SSL(self.host, self.port)
        mail_server.login(self.sender, self.sender_passwd)
        return mail_server
