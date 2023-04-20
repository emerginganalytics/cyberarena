import random
import string


class SubstitutionCipher:
    def __init__(self, message, key=None):
        self.message = message
        self.key = self._gen_alpha_key() if not key else key
        self.alpha = list(string.ascii_lowercase)

    def _gen_alpha_key(self):
        """Takes the standard alphabet and shuffles it to generate a randomized key"""
        rand_key = self.alpha.copy()
        random.shuffle(rand_key)

        return dict(zip(self.alpha, rand_key))

    def encrypt(self):
        ciphertext = []
        for letter in self.message:
            if letter not in self.alpha:
                ciphertext.append(letter)
                continue
            ciphertext.append(self.key.get(letter, letter))
        return {'ciphertext': ''.join(ciphertext), 'plaintext': self.message, 'key': self.key}

    def decrypt(self):
        cleartext = []
        for letter in self.message:
            if letter not in self.alpha:
                cleartext.append(letter)
                continue
            cleartext.append(self.key.get(letter, letter))
        return {'ciphertext': self.message, 'plaintext': ''.join(cleartext), 'key': self.key}
