import random
import string


def gen_alpha_key():
    standard_alpha = list(string.ascii_lowercase)
    rand_key = standard_alpha.copy()
    random.shuffle(rand_key)

    alpha_key = dict(zip(standard_alpha, rand_key))
    return alpha_key


def substitution_encrypt(message):
    alpha_key = gen_alpha_key()
    alpha = list(string.ascii_lowercase)
    ciphertext = []
    cleartext = message
    for letter in cleartext:
        if letter not in alpha:
            ciphertext.append(letter)
            continue
        ciphertext.append(alpha_key.get(letter, letter))

    cipher = {
        'ciphertext': ''.join(ciphertext),
        'cleartext': cleartext,
        'key': alpha_key
    }
    return cipher
