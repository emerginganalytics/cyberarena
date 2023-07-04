import os
import zipfile
import random
import string
import yaml
from enum import Enum


class CertManager:
    BASE_CERTS_LOCATION = 'certs'
    PASSWORD = "NMt95FB0szzKMZMoTc3Q"

    class CertFiles:
        YOUNGLING = 'youngling-cert.png'
        PADAWAN = 'padawan-cert.png'
        JEDI = 'jedi-master-cert.png'

    def __init__(self):
        self.password = self.PASSWORD

    def decrypt_youngling_cert(self):
        input_file = os.path.join('certs', f"{self.CertFiles.YOUNGLING}.zip")
        self._decrypt_cert(input_file=input_file, entry_name=self.CertFiles.YOUNGLING)

    def decrypt_padawan_cert(self):
        input_file = os.path.join('certs', f"{self.CertFiles.PADAWAN}.zip")
        self._decrypt_cert(input_file=input_file, entry_name=self.CertFiles.PADAWAN)

    def decrypt_jedi_cert(self):
        input_file = os.path.join('certs', f"{self.CertFiles.JEDI}.zip")
        self._decrypt_cert(input_file=input_file, entry_name=self.CertFiles.JEDI)

    def _decrypt_cert(self, input_file, entry_name):
        with zipfile.ZipFile(input_file, 'r', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.setpassword(self.password.encode('utf-8'))
            zip_file.extract(f"{entry_name}", path=os.path.join("certs"))
        zip_file.close()

    def _encrypt_cert(self, input_file, output_file):
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.setpassword(self.password.encode('utf-8'))
            zip_file.write(input_file)
        zip_file.close()
