#!/usr/bin/python3
import os
import time
import requests
import pwd
import subprocess


class AssessmentArtifacts:
    Q0_USER_CHECK = 'gigabyte'
    OLD_SOFTWARE = "liblog4j2-java/bionic,now 2.10.0-2"
    FILETYPE_CHECK = 'mp4'
    ADMIN_CHECK = 'noadmin_user'
    SUDOERS_STRING = "(ALL : ALL) ALL"


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
            response = requests.put(f"{self.url}{self.build_id}", json=data)
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


"""
This assessment is hard to maintain because the image will require many new patches in the future and the log4j
vulnerability is more difficult to find.
class Question1(Question):
    def __init__(self, build_id, url):
        super().__init__(build_id, url, 1)

    def unique_assessment(self):
        output = subprocess.run(['apt', 'list', '--installed'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        for line in output.split('\n'):
            if line.startswith(AssessmentArtifacts.OLD_SOFTWARE):
                return False
        return True
"""


class Question1(Question):
    """
    Assess over-privileged user
    """
    def __init__(self, build_id, url):
        super().__init__(build_id, url, 1)

    def unique_assessment(self):
        output = subprocess\
            .run(["sudo", "-l", "-U", AssessmentArtifacts.ADMIN_CHECK], stdout=subprocess.PIPE).stdout.decode('utf-8')
        if AssessmentArtifacts.SUDOERS_STRING in output:
            return False
        return True


class Question2(Question):
    """
    Assess banned File Type
    """
    def __init__(self, build_id, url):
        super().__init__(build_id, url, 2)

    def unique_assessment(self):
        output = subprocess.run(["find", "/", "-type", "f", "-name", "*.mp4"], stdout=subprocess.PIPE).stdout \
            .decode('utf-8')
        if AssessmentArtifacts.FILETYPE_CHECK in output:
            return False
        return True


def main():
    build_id = os.environ.get('BUILD_ID')
    url = f"https://{os.environ.get('URL')}"
    Question0(build_id=build_id, url=url).assess()
    Question1(build_id=build_id, url=url).assess()
    Question2(build_id=build_id, url=url).assess()


if __name__ == "__main__":
    main()
