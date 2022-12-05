from google.cloud import runtimeconfig
from sendgrid import SendGridAPIClient
import logging
from google.cloud import logging_v2
from sendgrid.helpers.mail import *
from templates import Templates

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class SendMail:

    def __init__(self):
        self.env = runtimeconfig.Client().config("cybergym")
        self.sendgrid_api_key = self.env.get_variable("SENDGRID_API_KEY").value.decode("utf-8")
        self.sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
        self.dns_suffix = self.env.get_variable('dns_suffix').value.decode("utf-8")

    def send_email(self, eml_subject, eml_to, eml_content):
        message = Mail()
        message.from_email = From(
            email=f"no-reply@trojan-cybergym.org" #{self.dns_suffix}"
        )
        message.subject = eml_subject
        message.content = eml_content
        message.to = eml_to

        try:
            response = self.sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)

    def from_template(self, msg_subject, msg_to):
        message = Mail()
        message.from_email = From(
            email=f"no-reply@trojan-cybergym.org"  # {self.dns_suffix}"
        )
        message.subject = Subject(
            subject=msg_subject.value
        )
        message.content = Templates().get_template(msg_subject)
        message.to = msg_to

        try:
            response = self.sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)
