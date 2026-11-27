#!/usr/local/lib/mailinabox/env/bin/python

# Reads in STDIN. If the stream is not empty, mail it to the system administrator.
# Subject lines (argv) are English gettext msgids; translated via the box-wide
# UI locale ($STORAGE_ROOT/ui_locale). Brand name "Trixiemail" stays untranslated.

import sys

import html
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# In Python 3.6:
#from email.message import Message

from utils import load_environment
import i18n

# Load system environment info.
env = load_environment()

# Process command line args. Subject is an English msgid (see daily_tasks.sh).
subject_msgid = sys.argv[1]
_ = i18n.gettext_for_locale(i18n.get_system_locale(env))
subject = _(subject_msgid)

# Administrator's email address.
admin_addr = "administrator@" + env['PRIMARY_HOSTNAME']

# Read in STDIN.
content = sys.stdin.read().strip()

# If there's nothing coming in, just exit.
if content == "":
    sys.exit(0)

# create MIME message
msg = MIMEMultipart('alternative')

# In Python 3.6:
#msg = Message()

msg['From'] = '"{}" <{}>'.format(env['PRIMARY_HOSTNAME'], admin_addr)
msg['To'] = admin_addr
msg['Subject'] = "[{}] {}".format(env['PRIMARY_HOSTNAME'], subject)

content_html = f'<html><body><pre style="overflow-x: scroll; white-space: pre;">{html.escape(content)}</pre></body></html>'

msg.attach(MIMEText(content, 'plain'))
msg.attach(MIMEText(content_html, 'html'))

# In Python 3.6:
#msg.set_content(content)
#msg.add_alternative(content_html, "html")

# send
smtpclient = smtplib.SMTP('127.0.0.1', 25)
smtpclient.ehlo()
smtpclient.sendmail(
        admin_addr, # MAIL FROM
        admin_addr, # RCPT TO
        msg.as_string())
smtpclient.quit()
