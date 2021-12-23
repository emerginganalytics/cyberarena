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
from Ciphers.caesarcipher import CaesarCipher
from Ciphers.ColTransposition import ColTransposition
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
        elif self.encryption == 'ColTransposition':
            return self.col_transposition()
        elif self.encryption == 'KeywordCipher':
            return self.dec_keyword_cipher()
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

    def col_transposition(self):
        self.plaintext = str(ColTransposition(message=self.message, keyword=self.keyword).decrypt)
        return self.plaintext

    def dec_keyword_cipher(self):
        """
        :return: str(plaintext of message encrypted with custom alphabet)

        This function is very similar to how the Caesar cipher works
        instead of using keys to shift the message, we use a keyword
        to make a custom alphabet where the keyword shifts all letters
        over. Any duplicates following the first occurrence of a letter
        are removed.
        :keyword 'keyword' produces 'KEYWORDABCFGHIJLMNPQSTUVXZ'

        :keyword 'CyberGym' produces 'CYBERGMADFHIJKLNOPQSTUVWXZ
        """
        keyword = ''
        standard_alpha = string.ascii_uppercase
        message = self.message.upper()

        # First remove any duplicate value from keyword
        for ch in self.keyword.upper():
            if ch not in keyword:
                keyword += ch
        # Remove duplicate values and append keyword and standard_alpha to create custom_alpha
        custom_alpha = keyword
        for ch in standard_alpha:
            if ch not in keyword:
                custom_alpha += ch
        # Pack the two alphabets into a list of tuples for easy access later
        alpha_key = list(zip(standard_alpha, custom_alpha))
        """
            Search for letter from message in alpha_key[1] and append the corresponding standard_alpha
            value to get plaintext.
        """
        for letter in message:
            if letter == " " or letter == '{' or letter == '}':
                self.plaintext += letter
            else:
                for item in alpha_key:
                    if letter in item[1]:
                        self.plaintext += item[0]
        return self.plaintext

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
