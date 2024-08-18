import smtplib
from email.mime.text import MIMEText
import LLMRetrieve
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def load_smtpconfig(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

smtpconfig = load_smtpconfig("../../config/smtp.json")

# calling these variables will run the LLMRetrieve file
subject = LLMRetrieve.email_subject
body = LLMRetrieve.email_body
sender = smtpconfig["email"]["username"]

# replace recipient field with the emails of actual travel agent emails
recipients = ["agastya.the.rocker@gmail.com"]
password = smtpconfig["email"]["password"]

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL(smtpconfig["email"]["smtp_server"], smtpconfig["email"]["port"]) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Sent")

send_email(subject, body, sender, recipients, password)
