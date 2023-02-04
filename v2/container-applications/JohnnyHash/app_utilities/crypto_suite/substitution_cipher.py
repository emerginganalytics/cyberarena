import random
import string


class SubstitutionCipher:
    def __init__(self, message):
        self.message = message

    @staticmethod
    def _gen_alpha_key():
        standard_alpha = list(string.ascii_lowercase)
        rand_key = standard_alpha.copy()
        random.shuffle(rand_key)

        return dict(zip(standard_alpha, rand_key))

    def substitution_encrypt(self):
        ciphertext = []
        cleartext = self.message
        alpha = list(string.ascii_lowercase)
        alpha_key = self._gen_alpha_key()

        for letter in cleartext:
            if letter not in alpha:
                ciphertext.append(letter)
                continue
            ciphertext.append(alpha_key.get(letter, letter))
        return {'ciphertext': ''.join(ciphertext), 'cleartext': cleartext, 'key': alpha_key}
