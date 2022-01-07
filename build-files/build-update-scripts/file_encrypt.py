import argparse
import io
import pyAesCrypt
from pathlib import Path


class FileEncrypt(object):
    """
    Used for encryption and decryption of PDF and YAML files.
    Requires pathlib.Path objects for both input and output directories

    Args:
        mode: Either type 'encrypt' or 'decrypt'
        input_dir: Where to insert the path iterator
        output_dir: Where to store the modified file
        pwd: Used to encrypt/decrypt the files
        ext: What file extension we are filtering over (pdf, (yaml, yml))
    """
    def __init__(self, mode, input_dir, output_dir, pwd, ext):
        self.mode = mode
        self.buffer_size = 65536
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.pwd = pwd
        self.ext = ext

        if self.ext in ['yaml', 'yml']:
            if self.mode == 'encrypt':
                self.encrypt_yamls()
            elif self.mode == 'decrypt':
                self.decrypt_yamls()
        else:
            self.walk_path()

    def encrypt_file(self, input_file, output_directory):
        """
        Takes Path file object and encrypts it using pyAesCrypt.encryptStream
        and returns places modified file in output_dir
        Args:
            input_file: Path file object
            output_directory: Path directory object to store modified file
        """
        print(f"[+] Encrypting {input_file.name}")
        output_file = output_directory / input_file.name
        with open(input_file, 'rb') as f:
            buffer_stream = io.BytesIO(f.read())

        output_buffer = io.BytesIO()
        pyAesCrypt.encryptStream(buffer_stream, output_buffer, self.pwd, self.buffer_size)

        with open(f'{output_file}.aes', 'wb') as f:
            f.write(output_buffer.getbuffer())

    def decrypt_file(self, input_file):
        """
            Function decrypts AES encrypted files and stores them in given output directory.
        """
        output_file = self.output_dir / input_file.name.strip(".aes")
        print(f"[+] Decrypting {input_file.name}")

        with open(input_file, 'rb') as f:
            buffer_stream = io.BytesIO(f.read())
        output_buffer = io.BytesIO()
        pyAesCrypt.decryptStream(buffer_stream, output_buffer, self.pwd, self.buffer_size,
                                 len(buffer_stream.getvalue()))

        with open(output_file, 'wb') as f:
            f.write(output_buffer.getbuffer())

    def encrypt_yamls(self):
        """
        Encrypting YAML files works the same way as encrypting PDF files.
        However, extra logic is needed to handle the current YAML nested
        directories.

        Encrypted files are sent to a new directory,
            <output_dir>/encrypted/<yaml_dir>
        """
        # Created directory if it doesn't already exist
        base_output_dir = self.output_dir / 'encrypted'
        if not base_output_dir.is_dir():
            Path.mkdir(base_output_dir)

        for cur_path in self.input_dir.iterdir():
            if cur_path.is_dir():
                # Create subdirectory if it doesn't already exist
                output_directory = base_output_dir / cur_path.name
                if not output_directory.is_dir():
                    Path.mkdir(output_directory)
                # Send subdir to iterator function and encrypt all
                # containing files matching extension
                self.walk_path(input_dir=cur_path, output_dir=output_directory)

    def decrypt_yamls(self):
        for cur_path in self.input_dir.iterdir():
            if cur_path.is_dir():
                self.walk_path(input_dir=cur_path)

    def walk_path(self, **kwargs):
        """
        Walks input_dir and calls encrypt_file for each file matching
        the desired file extension, self.ext. Due to how they are stored,
        YAML file encryption / decryption process requires calling this
        function multiple times.

        Args:
            **kwargs: input_dir, output_dir
        Returns:

        """
        input_dir = kwargs.get('input_dir', self.input_dir)
        output_dir = kwargs.get('output_dir', self.output_dir)

        for filename in input_dir.iterdir():
            if self.mode == 'encrypt':
                if filename.suffix == f'.{self.ext}':
                    self.encrypt_file(input_file=filename, output_directory=output_dir)
            elif self.mode == 'decrypt':
                file_ext = "".join(filename.suffixes)
                if file_ext == f'.{self.ext}.aes':
                    self.decrypt_file(input_file=filename)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--password', required=True, help='Password')
    parser.add_argument('-m', '--mode', required=True, choices=['encrypt', 'decrypt'])
    parser.add_argument('-e', '--extension', required=True, choices=['pdf', 'yaml', 'yml'])
    args = parser.parse_args()

    if args.extension in ['yaml', 'yml']:
        if args.mode == 'decrypt':
            input_directory = Path("../workout-specs")
            output_directory = Path("../workout-specs/needs-encrypted")
        else:
            input_directory = Path("../workout-specs/needs-encrypted")
            output_directory = Path("../workout-specs")
    else:
        if args.mode == 'decrypt':
            input_directory = Path("../workout-instructions/teacher-instructions")
            output_directory = Path("../workout-instructions/teacher-instructions/need-encrypted")
        else:
            input_directory = Path("../workout-instructions/teacher-instructions/need-encrypted")
            output_directory = Path("../workout-instructions/teacher-instructions")

    FileEncrypt(input_dir=input_directory, output_dir=output_directory,
                pwd=args.password, mode=args.mode, ext=args.extension)

if __name__ == "__main__":
    main()
