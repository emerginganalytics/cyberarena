import io
import os
import pyAesCrypt
import pathlib

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Andrew Bomberger"
__email__ = "abbomberger@ualr.edu"
__status__ = "Testing"


class CryptoLock:
    """

    """
    def __init__(self, plaintext_dir, encrypted_dir, lock_extension="pdf"):
        self.buffer_size = 65536
        self.plaintext_dir = plaintext_dir
        self.encrypted_dir = encrypted_dir
        self.pwd = os.environ.get("CYBER_ARENA_SPEC_PWD")
        if not self.pwd:
            reply = str(input(f"What password would you like to use for encryption? (To avoid this prompt, set the "
                              f"CYBER_ARENA_SPEC_PWD environment variable)"))
            self.pwd = reply
        self.lock_extension = lock_extension

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

        output_file = os.path.join(output_directory, input_file.name)
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
