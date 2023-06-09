#!/usr/bin/python3
import os
import time
import requests
import subprocess
import sys


def run():
    powershell_script = '''
    if((((Get-ADDefaultDomainPasswordPolicy).MinPasswordLength) -eq 12) -and (((Get-ADDefaultDomainPasswordPolicy).MaxPasswordAge.Days) -eq 365) -and (((Get-ADDefaultDomainPasswordPolicy).ComplexityEnabled) -eq "True")){
        Write-Output "True"
    }
    else{
        Write-Output "False"
    }
    '''

    process = subprocess.Popen(["powershell", "-Command", powershell_script], stdout=subprocess.PIPE)
    result = process.communicate()[0]

    output = result.decode("utf-8")
    return output


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
        properties = run()
        if properties == "True":
            return True
        return False


def main():
    url = f"https://{os.environ.get('URL')}"
    build_id = os.environ.get('BUILD_ID')
    Question0(build_id=build_id, url=url).assess()


if __name__ == "__main__":
    main()