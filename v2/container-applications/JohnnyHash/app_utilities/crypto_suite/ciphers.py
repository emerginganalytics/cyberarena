from app_utilities.crypto_suite.col_transposition import ColTransposition
from app_utilities.crypto_suite.caesarcipher import CaesarCipher, CaesarCipherError
from app_utilities.crypto_suite.substitution_cipher import SubstitutionCipher


class Ciphers:
    def __init__(self, algorithm):
        self.algorithm = algorithm
