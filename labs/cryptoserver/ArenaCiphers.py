'''
    The Decoder class is designed to provide students
    with the necessary functions needed to solve the
    Level 2 Arena challenges. This Class does not provide
    the means to encrypt / encode; Only the means to
    extract the plaintext from the ciphertext.

    Although the Arena page will be hosted by the same
    cloud controller, the page and subsequent challenges
    are designed to be separate from the normal CyberGym
    workouts.
'''
from caesarcipher import CaesarCipher
import base64
import string


class Decoder(object):
    def __init__(self, message=None, encryption=None, offset=False, key=None, keyword=None):
        self.message = message
        self.encryption = encryption
        self.offset = offset
        self.key = key
        self.keyword = keyword
        self.plaintext = ""
    '''
        if encryption == 'AtBash':
            self.atbash()
        elif encryption == 'Caesar':
            self.caesar()
        elif encryption == 'Base32':
            self.dec_base32()
        elif encryption == 'Base64':
            self.dec_base64()
        elif encryption == 'Col Transposition':
            self.transposition()
    '''
    def atbash(self):
        DECODE_TABLE = str.maketrans(
            string.ascii_lowercase,
            ''.join(reversed(string.ascii_lowercase)),
            string.whitespace)
        self.plaintext = str((self.message.lower()).translate(DECODE_TABLE))
        return str(self.plaintext)

    def caesar(self):
        self.plaintext = CaesarCipher(message=self.message, offset=self.key).decoded
        return str(self.plaintext)

    def dec_base64(self):
        try:
            self.plaintext = str(base64.b64decode(self.message.encode('UTF-8')))
        except ValueError:
            return "Invalid Chars: String is not a Base64 Decodable String..."
        return str(self.plaintext)

    def dec_base32(self):
        try:
            self.plaintext = str(base64.b32decode(self.message.encode('UTF-8')))
        except ValueError:
            return "Invalid Chars: String is not a Base32 Decodable String ..."
        return str(self.plaintext)

    '''
            The following functions necessary for decoding a Col Transposition
            cipher were borrowed from 
            http://www.crypto-it.net/eng/simple/columnar-transposition.html 
    '''
    def transposition(self):
        keyword = self.keyword
        matrix = self.create_transposition_matrix(self.get_keyword_sequence(keyword), self.message)

        for outer in range(len(matrix)):
            for inner in range(len(matrix[outer])):
                self.plaintext += matrix[outer][inner]
        return self.plaintext

    def create_transposition_matrix(self, keywordSequence, message):
        matrix = [[]]
        width = int(len(keywordSequence))
        height = int(len(message) / width)
        if height * width < len(message):
            height += 1
        matrix = self.create_empty_matrix(width, height, len(message))

        pos = 0
        for num in range(len(keywordSequence)):
            column = keywordSequence.index(num+1)

            r = 0
            while (r < len(matrix)) and (len(matrix[r]) > column):
                matrix[r][column] = message[pos]
                r += 1
                pos += 1
        return matrix

    def create_empty_matrix(self, width, height, matrix_length):
        matrix = []
        zero = 0

        for outer in range(height):
            matrix.append([])
            for inner in range(width):
                if zero >= matrix_length:
                    return matrix
                matrix[outer].append('')
                zero += 1
        return matrix

    def get_keyword_sequence(self, keyword):
        sequence = []

        for pos, ch in enumerate(keyword):
            prevLetters = keyword[:pos]
            newNumber = 1
            for prevPos, prevCh in enumerate(prevLetters):
                if prevCh > ch:
                    sequence[prevPos] += 1
                else:
                    newNumber += 1
            sequence.append(newNumber)
        return sequence
