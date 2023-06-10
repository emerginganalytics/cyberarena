import os
import zipfile
import random
import string
import yaml
from enum import Enum


class CertManager:
    BASE_CERTS_LOCATION = 'certs'
    USER_CERTS_LOCATION = os.path.join(os.path.expanduser('~'), 'Desktop')

    class CertFiles:
        YOUNGLING = 'youngling-cert.png'
        PADAWAN = 'padawan-cert.png'
        JEDI = 'jedi-master-cert.png'

    class ZippedCertFiles:
        YOUNGLING = os.path.join(os.path.expanduser('~'), 'Desktop', 'youngling-cert.png.zip')
        PADAWAN = os.path.join(os.path.expanduser('~'), 'Desktop', 'padawan-cert.png.zip')
        JEDI = os.path.join(os.path.expanduser('~'), 'Desktop', 'jedi-master-cert.png.zip')


    def __init__(self):
        self.password = self._get_password()
        self._initialize_certs()

    def decrypt_youngling_cert(self):
        self._decrypt_cert(input_file=self.ZippedCertFiles.YOUNGLING, entry_name=self.CertFiles.YOUNGLING)

    def decrypt_padawan_cert(self):
        self._decrypt_cert(input_file=self.ZippedCertFiles.PADAWAN, entry_name=self.CertFiles.PADAWAN)

    def decrypt_jedi_cert(self):
        self._decrypt_cert(input_file=self.ZippedCertFiles.JEDI, entry_name=self.CertFiles.JEDI)

    def _decrypt_cert(self, input_file, entry_name):
        with zipfile.ZipFile(input_file, 'r', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.setpassword(self.password.encode('utf-8'))
            zip_file.extract(f"certs/{entry_name}", path=self.USER_CERTS_LOCATION)
        zip_file.close()
        archive_file = os.path.join(self.USER_CERTS_LOCATION, 'include/certs', entry_name)
        new_file = os.path.join(self.USER_CERTS_LOCATION, entry_name)
        os.rename(archive_file, new_file)
        os.rmdir(os.path.join(self.USER_CERTS_LOCATION, 'include/certs'))

    def _encrypt_cert(self, input_file, output_file):
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.setpassword(self.password.encode('utf-8'))
            zip_file.write(input_file)
        zip_file.close()

    def _get_password(self):
        settings = yaml.safe_load(open('include/spec/settings.yaml'))
        password = settings.get('password', None)
        return password

    def _initialize_certs(self):
        for file in os.listdir(self.BASE_CERTS_LOCATION):
            if not file.endswith(".zip"):
                full_file_path = os.path.join(self.BASE_CERTS_LOCATION, file)
                self._encrypt_cert(full_file_path, os.path.join(self.USER_CERTS_LOCATION, f"{file}.zip"))
