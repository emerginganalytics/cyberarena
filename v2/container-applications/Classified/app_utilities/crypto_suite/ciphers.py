from enum import Enum

from app_utilities.crypto_suite.atbash import AtBash
from app_utilities.crypto_suite.caesarcipher import CaesarCipher, CaesarCipherError
from app_utilities.crypto_suite.col_transposition import ColTransposition
from app_utilities.crypto_suite.encodings import Encodings
from app_utilities.crypto_suite.keyword_cipher import KeywordCipher
from app_utilities.crypto_suite.railfence import RailFenceCipher
from app_utilities.crypto_suite.substitution_cipher import SubstitutionCipher
from app_utilities.globals import Algorithms, CipherModes



class Ciphers:
    """
    Handles creation and completion of General Cipher workouts.
    Interfaces with other cipher-based classes in crypto-suite
    """

    def __init__(self, algorithm, message, mode=CipherModes.DECRYPT, **kwargs):
        self.algorithm = algorithm
        self.mode = mode,
        self.message = message
        self.kwargs = kwargs
        # Finally get associated class for selected algorithm
        self.module = self._get_class()

    def _get_class(self):
        """
        Takes algorithm type and returns the associated class
        """
        if self.algorithm == Algorithms.CAESAR:
            return CaesarCipher
        elif self.algorithm == Algorithms.SUB:
            return SubstitutionCipher
        elif self.algorithm == Algorithms.COL:
            return ColTransposition
        elif self.algorithm == Algorithms.RAIL:
            return RailFenceCipher
        elif self.algorithm == Algorithms.ATBASH:
            return AtBash
        elif self.algorithm == Algorithms.KEYWORD:
            return KeywordCipher
        elif self.algorithm == Algorithms.BASE32:
            return Encodings(mode=self.mode, message=self.message).base32
        elif self.algorithm == Algorithms.BASE64:
            return Encodings(mode=self.mode, message=self.message).base64
        else:
            raise ValueError(f'Invalid cipher type : {self.algorithm}')

    def encrypt(self):
        if self.algorithm in [Algorithms.BASE32, Algorithms.BASE32]:
            # The encodings don't take any special arguments. Call the function and
            # return
            return self.module()
        else:
            pass
# [ eof ]
