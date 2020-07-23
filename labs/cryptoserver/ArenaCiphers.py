'''
    The Decoder class is designed to provide students
    with the necessary functions needed to solve the
    Level 2 Arena Cryptography challenges. This Class
    does not provide the means to encrypt / encode;
    Only the means to extract the plaintext from the
    ciphertext.

    Although the Arena page will be hosted by the same
    cloud controller, the page and subsequent challenges
    are designed to be separate from the normal CyberGym
    workouts.
'''
from caesarcipher import CaesarCipher
import base64
import string


class Decoder(object):
    def __init__(self, message=None, encryption=None, offset=None, key=None, keyword=None):
        self.message = message
        self.encryption = encryption
        self.offset = offset
        self.key = key
        self.keyword = keyword
        self.plaintext = ""

    def __repr__(self):
        if self.encryption == 'AtBash':
            return self.atbash()
        elif self.encryption == 'Caesar':
            return self.caesar()
        elif self.encryption == 'Base32':
            return self.dec_base32()
        elif self.encryption == 'Base64':
            return self.dec_base64()

    def atbash(self):
        '''
            AtBash is basically an overly simplified Affine cipher. Here we utilize
            the String library to first make a reversed alphabet which we can use to
            translate the ciphertext to the plaintext with the .translate(DECODE_TABLE)
            call
        '''
        DECODE_TABLE = str.maketrans(
            string.ascii_lowercase,
            ''.join(reversed(string.ascii_lowercase)),
            string.whitespace)
        self.plaintext = str((self.message.lower()).translate(DECODE_TABLE))
        return str(self.plaintext)

    def caesar(self):
        self.plaintext = CaesarCipher(message=self.message, offset=int(self.key)).decoded
        return str(self.plaintext)

    def dec_base64(self):
        try:
            self.plaintext = str(base64.b64decode(self.message).decode('UTF-8'))
        except ValueError:
            return "Invalid Chars: String is not a Base64 Decodable String..."
        return str(self.plaintext)

    def dec_base32(self):
        try:
            self.plaintext = str(base64.b32decode(self.message).decode('UTF-8'))
        except ValueError:
            return "Invalid Chars: String is not a Base32 Decodable String ..."
        return str(self.plaintext)
