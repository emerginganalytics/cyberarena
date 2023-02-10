import copy
import io
import json
import os
import pyAesCrypt
import pathlib
import hashlib
import sys

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Andrew Bomberger"
__email__ = "abbomberger@ualr.edu"
__status__ = "Testing"


class CryptoLock:
    def __init__(self, plaintext_dir, encrypted_dir, lock_extension="pdf"):
        self.buffer_size = 65536
        self.plaintext_dir = plaintext_dir
        self.plaintext_hashes_file = os.path.join(self.plaintext_dir, 'file_hashes.json')
        self.encrypted_dir = encrypted_dir
        self.pwd = os.environ.get("CYBER_ARENA_SPEC_PWD")
        if not self.pwd:
            reply = str(input(f"What password would you like to use for encryption? (To avoid this prompt, set the "
                              f"CYBER_ARENA_SPEC_PWD environment variable)"))
            self.pwd = reply
        self.lock_extension = lock_extension
        self.force_encryption = False
        self.file_hashes = self._load_file_hashes()
        self.hash_dict = copy.deepcopy(self.file_hashes)

    def encrypt_dir(self):
        for item in os.scandir(self.plaintext_dir):
            if item.is_dir():
                child_plaintext_dir = item.path
                child_encrypted_dir = os.path.join(self.encrypted_dir, item.name)
                if not os.path.isdir(child_encrypted_dir):
                    os.mkdir(child_encrypted_dir)
                for file in os.scandir(child_plaintext_dir):
                    self._encrypt_file(file, child_encrypted_dir)
            if item.is_file():
                self._encrypt_file(item, self.plaintext_dir)

        # Encryption process is complete; Update json file if needed
        self._update_file_hashes()

    def decrypt_dir(self):
        for item in os.scandir(self.encrypted_dir):
            if item.is_dir():
                child_encrypted_dir = item.path
                child_plaintext_dir = os.path.join(self.plaintext_dir, item.name)
                if not os.path.isdir(child_plaintext_dir):
                    os.mkdir(child_plaintext_dir)
                for file in os.scandir(child_encrypted_dir):
                    self._decrypt_file(file, child_plaintext_dir)
            if item.is_file():
                if item.name.split(".")[-2] == f"{self.lock_extension}":
                    self._decrypt_file(item, self.plaintext_dir)

    def _encrypt_file(self, input_file, output_directory):
        """
        Takes Path file object and encrypts it using pyAesCrypt.encryptStream
        and returns places modified file in output_dir
        Args:
            input_file: Path file object
            output_directory: Path directory object to store modified file
        """
        if pathlib.Path(input_file).suffix != f".{self.lock_extension}":
            return False

        # If the file hashes of plaintext and newly decrypted file don't compare, encrypt
        output_file = os.path.join(output_directory, input_file.name)
        compare_file_hashes = False
        if not self.force_encryption:
            compare_file_hashes = self._compare_file_hashes(input_file, input_file.name)
        if not compare_file_hashes:
            with open(input_file, 'rb') as f:
                buffer_stream = io.BytesIO(f.read())

            output_buffer = io.BytesIO()
            pyAesCrypt.encryptStream(buffer_stream, output_buffer, self.pwd, self.buffer_size)

            with open(f'{output_file}.aes', 'wb') as f:
                f.write(output_buffer.getbuffer())

    def _decrypt_file(self, input_file, output_directory):
        """
            Function decrypts AES encrypted files and stores them in given output directory.
        """
        try:
            if not input_file.name.split(".")[-2] == f"{self.lock_extension}":
                return False
        except IndexError:
            print(f"WARNING: Potentially unencrypted file in the encrypted directory: {input_file.name}")
            exit(1)
        output_file = os.path.join(output_directory, input_file.name[:-len(".aes")])
        with open(input_file, 'rb') as f:
            buffer_stream = io.BytesIO(f.read())

        output_buffer = io.BytesIO()
        pyAesCrypt.decryptStream(buffer_stream, output_buffer, self.pwd, self.buffer_size,
                                 len(buffer_stream.getvalue()))

        with open(output_file, 'wb') as f:
            f.write(output_buffer.getbuffer())

    def _compare_file_hashes(self, new_file, file_name):
        """
        Encryption =>
            True: Current file compares; no need to encrypt
            False: Hash deviates; Safe to encrypt
        :param new_file: Path of file you want to compare
        :param file_name: name of old file you want to grab the hash for
        :return: Bool
        """
        old_hash = self.hash_dict.get(file_name, False)
        new_hash = self._calculate_file_hash(new_file)
        if old_hash:
            if new_hash == old_hash:
                return True
        print(f'\t...Updated hash {file_name} : {new_hash}')
        self.hash_dict[file_name] = new_hash
        return False

    @staticmethod
    def _calculate_file_hash(file_path):
        """
        Takes path of file to calculate the md5 hash for and returns
        the calculated hash
        :param file_path => str():
        :return: file md5 hash
        """
        with open(file_path, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_returned = hashlib.md5(data).hexdigest()
        return md5_returned

    def _generate_file_hashes(self):
        """
        Called during cases where the file_hashes.json file either doesn't exist or exists, but is empty
        Iterates through existing plaintext files and generates a dictionary of hashes for each file
        :return: dict of plaintext file hashes
        """
        print('\t...Creating json file')
        file_hashes = dict()
        for item in os.scandir(self.plaintext_dir):
            if item.is_dir():
                for file in os.scandir(item.path):
                    file_hashes[file.name] = self._calculate_file_hash(file)
            if item.is_file():
                file_hashes[item.name] = self._calculate_file_hash(item)
        self.hash_dict = file_hashes

    def _update_file_hashes(self):
        """
        Populates file_hashes.json with calculated local plaintext file hashes.
        If file and hash_dict are the same, no need to update the file
        :return:
        """
        if (self.file_hashes != self.hash_dict) or self.force_encryption:
            print('\t...Updating Local File Hashes')
            with open(self.plaintext_hashes_file, 'w+') as f:
                json.dump(self.hash_dict, f, indent=4)
        return False

    def _load_file_hashes(self):
        """
        Takes the file_hashes file path and loads the contents into a JSON object
        If the file is empty or does not exist, raise warning, generate file, and exit
        :return: dict()
        """
        if os.path.exists(self.plaintext_hashes_file):
            if not os.stat(self.plaintext_hashes_file).st_size == 0:
                with open(self.plaintext_hashes_file) as f:
                    file_contents = json.load(f)
                return file_contents

        print('\nWARNING: Either json file does not exist or file is empty! Sync specifications before continuing')
        # File is empty or does not exist. Generate json hash file
        self.file_hashes = dict()
        self._generate_file_hashes()
        # Force Encryption of all plaintext files
        self.force_encryption = True
        self.encrypt_dir()
        exit(1)
