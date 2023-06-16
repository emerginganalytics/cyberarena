#!/usr/bin/python3
import os
import time
import requests
import pwd
import subprocess


class AssessmentArtifacts:
    """
    Specify key values to search for (environment variables, system objects or commands, etc.."""
    pass


class Question:
    """
    This is the parent class used for additional assessment questions.
    """
    def __init__(self, build_id, url, question_number):
        self.build_id = build_id
        self.url = url
        self.question_key = os.environ.get(f'Q_{question_number}_KEY')
        self.complete_file = f"signal_{question_number}_complete"

    def assess(self):
        if not os.path.exists(self.complete_file):
            if self.unique_assessment():
                self._mark_complete()

    def unique_assessment(self):
        pass

    def _mark_complete(self):
        if not os.path.exists(self.complete_file):
            data = {
                "question_key": self.question_key,
            }
            response = requests.put(f"http://{self.url}{self.build_id}", json=data)
            if response and response.status_code == 200:
                open(self.complete_file, 'a').close()

class Question0(Question):
    """
    Assess whether the Gigabyte user is deleted
    """
    def __init__(self, build_id, url):
        super().__init__(build_id, url, 0)

    def unique_assessment(self):
        for p in pwd.getpwall():
            if p[0] == AssessmentArtifacts.Q0_USER_CHECK:
                return False
        return True


def main():
    url = os.environ.get('URL')
    build_id = os.environ.get('BUILD_ID')
    Question0(build_id=build_id, url=url).assess()


if __name__ == "__main__":
    main()
