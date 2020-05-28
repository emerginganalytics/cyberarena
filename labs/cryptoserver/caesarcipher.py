from random import randrange
import string
import math
import logging


class CaesarCipher(object):
    def __init__(self, message=None, encode=False, decode=False, offset=False,
                 crack=None, verbose=None, alphabet=None):
        """
        A class that encodes, decodes and cracks strings using the Caesar shift
        cipher.

        Accepts messages in a string and encodes or decodes by shifting the
        value of the letter by an arbitrary integer to a different letter in
        the alphabet provided.

        http://en.wikipedia.org/wiki/Caesar_cipher

        Do not ever use this for real communication, but definitely use it for
        fun events like the Hacker Olympics.

        Attributes:
            message: The string you wish to encode.
            encode: A boolean indicating desire to encode the string, used as
                command line script flag.
            decoded: A boolean indicating desire to decode the string, used as
                command line script flag.
            cracked: A boolean indicating to desire to crack the string, used
                as command line script flag.
            verbose: A boolean indicating the desire to turn on debug output,
                use as command line script flag.
            offset: Integer by which you want to shift the value of a letter.
            alphabet: A tuple containing the ASCII alphabet in uppercase.

        Examples:
            Encode a string with a random letter offset.
            >>> cipher = CaesarCipher('I want to encode this string.')
            >>> cipher.encoded
            'W kobh hc sbqcrs hvwg ghfwbu.'

            Encode a string with a specific letter offset.
            >>> cipher = CaesarCipher('I want to encode this string.',
            ...     offset=14)
            >>> cipher.encoded
            'W kobh hc sbqcrs hvwg ghfwbu.'


            Decode a string with a specific letter offset.
            >>> cipher = CaesarCipher('W kobh hc sbqcrs hvwg ghfwbu.',
            ...    offset=14)
            >>> cipher.decoded
            'I want to encode this string.'

            Crack a string of ciphertext without knowing the letter offset.
            >>> cipher = CaesarCipher('W kobh hc sbqcrs hvwg ghfwbu.')
            >>> cipher.cracked
            'I want to encode this string.'
        """
        self.message = message
        self.encode = encode
        self.decode = decode
        self.offset = offset
        self.verbose = verbose
        self.crack = crack
        self.alphabet = alphabet

        # Frequency of letters used in English, taken from Wikipedia.
        # http://en.wikipedia.org/wiki/Letter_frequency
        self.frequency = {
            'a': 0.08167,
            'b': 0.01492,
            'c': 0.02782,
            'd': 0.04253,
            'e': 0.130001,
            'f': 0.02228,
            'g': 0.02015,
            'h': 0.06094,
            'i': 0.06966,
            'j': 0.00153,
            'k': 0.00772,
            'l': 0.04025,
            'm': 0.02406,
            'n': 0.06749,
            'o': 0.07507,
            'p': 0.01929,
            'q': 0.00095,
            'r': 0.05987,
            's': 0.06327,
            't': 0.09056,
            'u': 0.02758,
            'v': 0.00978,
            'w': 0.02360,
            'x': 0.00150,
            'y': 0.01974,
            'z': 0.00074}

        # Get ASCII alphabet if one is not provided by the user.
        if alphabet is None:
            self.alphabet = tuple(string.ascii_lowercase)

    def cipher(self):
        """Applies the Caesar shift cipher.

        Based on the attributes of the object, applies the Caesar shift cipher
        to the message attribute. Accepts positive and negative integers as
        offsets.

        Required attributes:
            message
            offset

        Returns:
            String with cipher applied.
        """
        # If no offset is selected, pick random one with sufficient distance
        # from original.
        if self.offset is False:
            self.offset = randrange(5, 25)
            logging.info("Random offset selected: {0}".format(self.offset))
        logging.debug("Offset set: {0}".format(self.offset))

        # Cipher
        ciphered_message_list = list(self.message)
        for i, letter in enumerate(ciphered_message_list):
            if letter.isalpha():
                # Use default upper and lower case characters if alphabet
                # not supplied by user.
                if letter.isupper():
                    alphabet = [character.upper()
                                for character in self.alphabet]
                else:
                    alphabet = self.alphabet

                logging.debug("Letter: {0}".format(letter))
                logging.debug("Alphabet: {0}".format(alphabet))
                value = alphabet.index(letter)
                cipher_value = value + self.offset
                if cipher_value > 25 or cipher_value < 0:
                    cipher_value = cipher_value % 26
                logging.debug("Cipher value: {0}".format(cipher_value))
                ciphered_message_list[i] = alphabet[cipher_value]
                logging.debug("Ciphered letter: {0}".format(letter))
        self.message = ''.join(ciphered_message_list)
        return self.message

    def calculate_entropy(self, entropy_string):
        """Calculates the entropy of a string based on known frequency of
        English letters.

        Args:
            entropy_string: A str representing the string to calculate.

        Returns:
            A negative float with the total entropy of the string (higher
            is better).
        """
        total = 0
        for char in entropy_string:
            if char.isalpha():
                prob = self.frequency[char.lower()]
                total += - math.log(prob) / math.log(2)
        logging.debug("Entropy score: {0}".format(total))
        return total

    @property
    def cracked(self):
        """Attempts to crack ciphertext using frequency of letters in English.

        Returns:
            String of most likely message.
        """
        logging.info("Cracking message: {0}".format(self.message))
        entropy_values = {}
        attempt_cache = {}
        message = self.message
        for i in range(25):
            self.message = message
            self.offset = i * -1
            logging.debug("Attempting crack with offset: "
                          "{0}".format(self.offset))
            test_cipher = self.cipher()
            logging.debug("Attempting plaintext: {0}".format(test_cipher))
            entropy_values[i] = self.calculate_entropy(test_cipher)
            attempt_cache[i] = test_cipher

        sorted_by_entropy = sorted(entropy_values, key=entropy_values.get)
        self.offset = sorted_by_entropy[0] * -1
        cracked_text = attempt_cache[sorted_by_entropy[0]]
        self.message = cracked_text

        logging.debug("Entropy scores: {0}".format(entropy_values))
        logging.debug("Lowest entropy score: "
                      "{0}".format(str(entropy_values[sorted_by_entropy[0]])))
        logging.debug("Most likely offset: {0}".format(self.offset))
        logging.debug("Most likely message: {0}".format(cracked_text))

        return cracked_text

    @property
    def encoded(self):
        """Encodes message using Caesar shift cipher

        Returns:
            String encoded with cipher.
        """
        logging.info("Encoding message: {0}".format(self.message))
        return self.cipher()

    @property
    def decoded(self):
        """Decodes message using Caesar shift cipher

        Inverse operation of encoding, applies negative offset to Caesar shift
        cipher.

        Returns:
            String decoded with cipher.
        """
        logging.info("Decoding message: {0}".format(self.message))
        self.offset = self.offset * -1
        return self.cipher()


class CaesarCipherError(Exception):
    def __init__(self, message):
        logging.error("ERROR: {0}".format(message))
        logging.error("Try running with --help for more information.")
