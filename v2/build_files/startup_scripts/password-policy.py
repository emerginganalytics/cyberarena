#!/usr/bin/python3
import os
import time
import requests
import pwd
import subprocess
import pyad


class AssessmentArtifacts:
    Q0_USER_CHECK = 'gigabyte'
    OLD_SOFTWARE = "liblog4j2-java/bionic,now 2.10.0-2"
    FILETYPE_CHECK = 'mp4'
    ADMIN_CHECK = 'philip'
    SUDOERS_STRING = "(ALL : ALL) ALL"
    CRONTAB_STRING = "philip    ALL=(ALL:ALL) ALL"


def directory_setup():
    pyad.set_defaults(ldap_server='cybergym.com')
    ad_query = pyad.adquery.ADQuery()
    ad_query.execute_query(
        attributes=["maxPwdAge", "minPwdLength", "complexityEnabled"],
        where_clause="objectClass='domain'"
    )
    for row in ad_query.get_results():
        max_password_age = row["maxPwdAge"]
        minimum_password_length = row["minPwdLength"]
        password_complexity = row["complexityEnabled"]
    return[max_password_age, minimum_password_length, password_complexity]


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
        properties = directory_setup()
        max_password_age = properties[0]
        minimum_password_length = properties[1]
        password_complexity = properties[2]
        if max_password_age == 365 and minimum_password_length == 12 and password_complexity is True:
            return True
        return False


def main():
    url = f"https://{os.environ.get('URL')}"
    build_id = os.environ.get('BUILD_ID')
    Question0(build_id=build_id, url=url).assess()


if __name__ == "__main__":
    main()
