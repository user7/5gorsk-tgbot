import sys
import sysaudit
import json
from smtplib import SMTP_SSL
from smtplib import SMTPException
from email.mime.text import MIMEText
from email import utils

def conf_load(filename):
    with open(filename, 'r', encoding = 'utf-8') as f:
        return json.load(f)

c = conf_load('config.json')['email']
email_host = c['host']
email_port = int(c['port'])
email_login = c['login']
email_pass = c['pass']

text = 'supertest'
if len(sys.argv) > 1:
    text = sys.argv[1]

with SMTP_SSL(host = email_host, port = email_port) as smtp:
    fro = utils.formataddr(('Неодим 2', email_login), charset='utf-8')
    to = 'brankovic@yandex.ru'
    print(smtp.login(email_login, email_pass))
    msg = MIMEText(text)
    msg['Subject'] = 'test subject'
    msg['From'] = fro
    msg['To'] = to
    try:
        smtp.sendmail(f'{email_login}', to, msg.as_string())
    except SMTPException as e:
        print(f'sendmail failed: {e}')
    print(smtp.quit())

