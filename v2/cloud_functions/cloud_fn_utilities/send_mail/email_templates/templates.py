import os
from sendgrid.helpers.mail import *
from enum import Enum


class Subjects(Enum):
    Expired = "Virtual Machine About to Expire"


class Templates:
    def __init__(self):
        self.subjects = Subjects

    def get_template(self, eml_subject):
        if eml_subject.value == self.subjects.Expired.value:
            filepath = os.path.dirname(os.path.abspath(__file__))
            file = open(f"{filepath}/expired.txt", "r")
            eml_content = Content(
                content=file.read(),
                mime_type="text/plain"
            )
            return eml_content

