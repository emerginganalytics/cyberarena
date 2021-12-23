# Copied from http://gauravvichare.com/how-to-password-protect-pdf-file-using-python/

import PyPDF2
import argparse
from pathlib import Path


def set_teacher_instruction_password(input_file, user_pass, output_directory):
    """
    Function encrypts plain text teacher instruction pdfs and saves them as encrypted pdfs, which
    get copied over to cloud storage for use in the workouts.
    """

    output_file = output_directory / input_file.name

    output = PyPDF2.PdfFileWriter()

    input_stream = PyPDF2.PdfFileReader(open(input_file, "rb"))

    for i in range(0, input_stream.getNumPages()):
        output.addPage(input_stream.getPage(i))

    outputStream = open(output_file, "wb")

    # Set user password to pdf file
    output.encrypt(user_pass, use_128bit=True)
    output.write(outputStream)
    outputStream.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--password', required=True, help='Password')

    args = parser.parse_args()

    input_directory = Path("../build-files/teacher-instructions/need-encryption")
    output_directory = Path("../build-files/teacher-instructions")
    for filename in input_directory.iterdir():
        if filename.suffix == ".pdf":
            print(f"Encrypting {filename.name}")
            set_teacher_instruction_password(filename, args.password, output_directory)


if __name__ == "__main__":
    main()