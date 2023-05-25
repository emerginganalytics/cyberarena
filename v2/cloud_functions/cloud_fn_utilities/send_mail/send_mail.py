from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from cloud_fn_utilities.send_mail.email_templates.templates import Templates
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from google.cloud import runtimeconfig
import base64

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

# TODO: Add SendGrid API key to cloud_fn CloudEnv class,
#   remove unused call to env: line 25 and 26
#   reformat runtimeconfig calls ln 26 and 30 to pull from CloudEnv class instead


class SendMail:
    def __init__(self, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.config = runtimeconfig.Client().config("cybergym")
        self.ds = DataStoreManager()
        self.sendgrid_api_key = self.config.get_variable("SENDGRID_API_KEY").value.decode("utf-8")
        self.sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
        self.dns_suffix = self.config.get_variable('dns_suffix').value.decode("utf-8")

    def send_email(self, eml_subject, eml_to, eml_content=None, eml_attachment=None):
        message = Mail()
        message.from_email = From(
            email=f"no-reply@trojan-cybergym.org"  # {self.dns_suffix}"
        )
        message.subject = eml_subject
        message.to = eml_to

        if eml_content:
            message.content = eml_content
        if eml_attachment:
            message.attachment = eml_attachment

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

    def send_expiring_units(self, unit_id, workout_name, instructor, num_workouts, hours_until_expires):
        """
        sends an email to the provided instructor's email that the unit is about to expire
        @return:
        """
        project = self.env_dict['project']
        eml_subject = Subject(f"Unit in {project} about to expire")
        eml_to = To(instructor)
        eml_content = Content(
            mime_type="text",
            content=f"Unit id: {unit_id}\n"
                    f"Name: {workout_name}\n"
                    f"Project: {project}\n"
                    f"Number of Workouts: {num_workouts}\n"
                    f"Expires in {hours_until_expires} hours\n"
        )
        self.send_email(eml_subject=eml_subject, eml_to=eml_to, eml_content=eml_content)

    def send_help_form(self, usr_email, usr_subject, usr_message, usr_image=None):
        """
        Used in the webapp's help form. Sends the users request to all the admins associated with the project.
        @return:
        """
        admins = self.ds.get_admins()
        eml_to = []
        for admin in admins:
            eml_to.append(To(email=admin['email']))

        eml_subject = Subject(usr_subject)
        eml_content = Content(
            mime_type="text",
            content=f"Email from user {usr_email} \n"
                    f"{usr_message}"
        )

        eml_attachment = None
        if usr_image:
            data = base64.b64encode(usr_image.read()).decode()
            eml_attachment = Attachment(
                file_content=FileContent(data),
                file_name=FileName(usr_image.filename),
                file_type=FileType(usr_image.content_type),
                disposition=Disposition("attachment")
            )

        self.send_email(eml_subject=eml_subject, eml_to=eml_to, eml_content=eml_content, eml_attachment=eml_attachment)
