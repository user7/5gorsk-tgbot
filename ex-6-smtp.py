import json
from smtplib import SMTP_SSL

def conf_load(filename):
    with open(filename, 'r', encoding = 'utf-8') as f:
        return json.load(f)

c = conf_load('config.json')["email"]
email_host = c["host"]
email_port = int(c["port"])
email_login = c["login"]
email_pass = c["pass"]

with SMTP_SSL(host = email_host, port = email_port) as smtp:
    print(smtp.login(email_login, email_pass))
    print(smtp.sendmail(
        email_login, # same as sending address
        ["brankovic@ya.ru"],
        "Hello test 10"))
    print(smtp.quit())

