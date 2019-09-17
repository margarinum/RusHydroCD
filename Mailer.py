#!/usr/bin/python3.6

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

warnMessage = "Rushydro {} will be updated to {} on server {}"
infoMessage = "Rushydro {} {} available to update on server {}"
updMessage = "Rushydro {} updated to {} on server {}"
alertMessage = "Rushydro {} not running on {}"
subjects = {'info': 'Rushydro Info', 'alert': 'Rushydro Alert'}

recipientsWarning = ["margarinum@gmail.com"]
recipientsUpdate = ["margarinum@gmail.com"]
recipientsInfo = ["margarinum@gmail.com"]
recipientsAlert = ["margarinum@gmail.com"]


class Mailer(object):
    # Волшебный конструктор с резиновым массивом **kwargs
    def __init__(self, mailType, **kwargs):
        self.smtpServer = 'smtp.gmail.com: 587'
        self.senderEmail = "rushydroupdater@gmail.com"
        self.password = "unidataplatform"
        self.recepients = ''
        self.mailType = mailType
        self.subject = None
        self.message = None
        # Такой же резиновый сеттер по всему массиву - pythonic way
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.generateMessage()


    # Генератор письма
    def generateMessage(self):
        if self.mailType == 'warn':
            self.subject = subjects['info']
            self.message = warnMessage.format(self.repo, self.tag, self.ip)
            self.recepients = recipientsWarning
        elif self.mailType == 'info':
            self.subject = subjects['info']
            self.message = infoMessage.format(self.repo, self.tag, self.ip)
            self.recepients = recipientsInfo
        elif self.mailType == 'upd':
            self.subject = subjects['info']
            self.message = updMessage.format(self.repo, self.tag, self.ip)
            self.recepients = recipientsUpdate
        elif self.mailType == 'alert':
            self.subject = subjects['alert']
            self.message = alertMessage.format(self.component, self.ip)
            self.recepients = recipientsAlert

    def send(self):
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.message, 'plain'))
        server = smtplib.SMTP(self.smtpServer)
        server.starttls()
        server.login(self.senderEmail, self.password)
        server.sendmail(self.senderEmail, ", ".join(self.recepients), msg.as_string())
        server.quit()

'''
#Костыльная реализация деревянных геттера и сеттера

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, params):
        self._options = {'repo': params['repo'],
                         'ip': params['ip'],
                         'tag': params['tag'],
                         'component': params['component']}
'''