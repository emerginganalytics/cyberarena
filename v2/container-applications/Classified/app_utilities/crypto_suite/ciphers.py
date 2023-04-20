import logging

from app_utilities.crypto_suite.affine import Affine
from app_utilities.crypto_suite.caesarcipher import CaesarCipher, CaesarCipherError
from app_utilities.crypto_suite.col_transposition import ColTransposition
from app_utilities.crypto_suite.encodings import Encodings
from app_utilities.crypto_suite.keyword_cipher import KeywordCipher
from app_utilities.crypto_suite.railfence import RailFenceCipher
from app_utilities.crypto_suite.substitution_cipher import SubstitutionCipher
from app_utilities.globals import Algorithms, CipherModes


class Ciphers(object):
    """
    Handles creation and completion of General Cipher workouts.
    Interfaces with other cipher-based classes in crypto-suite
    """

    def __init__(self, algorithm, message, mode, key):
        self.algorithm = algorithm
        self.mode = mode
        self.message = message
        self.key = key
        self.output = dict()
        self.module = None

    def get(self):
        """
        Sets the cipher module to use and returns the output based on input CipherMode.
        :returns: dict() => {'ciphertext', 'plaintext', 'key'}
        """
        self._set_module()
        if self.algorithm not in [Algorithms.BASE32, Algorithms.BASE64]:
            if self.mode is CipherModes.ENCRYPT:
                self.output = self.module.encrypt()
            elif self.mode is CipherModes.DECRYPT:
                self.output = self.module.decrypt()
            else:
                logging.error(f'Unrecognized mode, {self.mode} for Cipher {self.algorithm.value.lower()}')
                raise ValueError
        return self.output

    def _set_module(self):
        if self.algorithm == Algorithms.CAESAR:
            self.module = CaesarCipher(message=self.message, offset=int(self.key))
        elif self.algorithm == Algorithms.SUB:
            self.module = SubstitutionCipher(message=self.message, key=self.key)
        elif self.algorithm == Algorithms.COL:
            self.module = ColTransposition(message=self.message, keyword=self.key)
        elif self.algorithm == Algorithms.RAIL:
            self.module = RailFenceCipher(message=self.message, key=self.key)
        elif self.algorithm == Algorithms.ATBASH:
            self.module = Affine(message=self.message, key=self.key, atbash=True)
        elif self.algorithm == Algorithms.AFFINE:
            # Expects key to contain keys, 'key_1' and 'key_2'
            self.module = Affine(message=self.message, key=self.key, atbash=False)
        elif self.algorithm == Algorithms.KEYWORD:
            self.module = KeywordCipher(message=self.message, key=self.key)
        elif self.algorithm == Algorithms.BASE32:
            self.output = Encodings(mode=self.mode, message=self.message).base32()
        elif self.algorithm == Algorithms.BASE64:
            self.output = Encodings(mode=self.mode, message=self.message).base64()

    @staticmethod
    def options():
        return [i.name for i in Algorithms]
# [ eof ]
