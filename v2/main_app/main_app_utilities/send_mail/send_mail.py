from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
import base64

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class SendMail:
    def __init__(self, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.ds = DataStoreManager()
        self.sendgrid_api_key = self.env.sendgrid_api_key
        self.sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
        self.dns_suffix = self.env.dns_suffix

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

    def send_help_form(self, usr_email, usr_subject, usr_message, usr_image=None):
        """
        Used in the webapp's help form. Sends the users request to all the admins associated with the project.
        @return:
        """
        admins = ArenaAuthorizer().get_admins()
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
