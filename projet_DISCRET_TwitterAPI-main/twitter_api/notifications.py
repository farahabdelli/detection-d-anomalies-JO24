import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from twitter_api import collection_logging
from datetime import datetime
from query_settings import emailParams

execution_time = time.strftime("%Y%m%d-%H%M%S")

class EmailSession():
    def __init__(self, email_params, type_email):
        #Paramètres pour les alertes e-mail
        self.sender_email = email_params.sender_email
        self.password = email_params.password
        self.receiver_emails = email_params.receiver_emails
        type_to_txt = {1: 'ERREUR', 2: 'REPRISE', 3: 'DÉROULEMENT OK'}
        self.subject = '[{}] {} {}'.format(type_to_txt[type_email], email_params.subject, execution_time)
        self.server = self.setup_email_server()
        self.msg = self.setup_email()

    def close(self):
        self.server.quit()

    #Envoie une alerte par mail
    def sendMail(self, msgContent):
        for mail in self.msg:
            mail.attach(MIMEText(msgContent, 'plain'))
            text = mail.as_string()
            self.server.sendmail(self.sender_email, mail['To'], text)

    def setup_email(self):
        tab = []
        for receiver in self.receiver_emails:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver
            msg['Subject'] = self.subject
            tab.append(msg)
        return tab

    def setup_email_server(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.sender_email, self.password)
        return server

def send_alive_email():
    email_session = EmailSession(emailParams, 3)
    email_session.sendMail('La collecte se déroule correctement.')
    email_session.close()

def send_reprise_email():
    messageContent = 'Reprise de la collecte à {}.'.format(datetime.now())
    email_session = EmailSession(emailParams, 2)
    email_session.sendMail(messageContent)
    email_session.close()

def send_error_email(messageContent):
    email_session = EmailSession(emailParams, 1)
    email_session.sendMail(messageContent)
    email_session.close()



