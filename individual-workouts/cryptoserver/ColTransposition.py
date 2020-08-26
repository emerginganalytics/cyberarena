"""
    Thanks to JamesLyons (https://github.com/jameslyons/pycipher/blob/master/pycipher/columnartransposition.py#L45)
    for part of the logic used to encrypt and decrypt the column transposition cipher.
"""
import math
import re

class ColTransposition(object):
    def __init__(self, message=None, keyword=None, encrypt=False, decrypt=True):
        """
                This Class takes the message and a keyword to encipher or decipher
                Regular Column Transposition Ciphers.

                For ease, the all keywords will be converted to upper and all spaces
                will be stripped before the encryption process starts. To prevent
                character loss and ensure plaintext readability, encode the plaintext with
                base64 before encrypting.

                The ciphertext is created by taking the keyword and placing it in a
                list to be the cipher matrix column headers. We then determine which
                order the columns will be displayed by sorting the keyword in
                alphabetical order. If there are multiples of the same letter, any
                subsequent appearance will be denoted by n+1 with n being the
                previous count value for the character.

                The cipher matrix is determined by width = len(Keyword) and
                height = math.ceil(ciphertext / width))

                Example::
                    :Keyword: ZEBRAS
                    :Ciphertext: We are discovered
                    yields a matrix with WxH being 6x(15 % 6) or 6x3

                    |Z|E|B|R|A|S|
                    -------------
                    |W|E|A|R|E|D|
                    |I|S|C|O|V|E|
                    |R|E|D| | | |
                    -------------

                    Using the above matrix,
                        :Ciphertext: = "ev acd ese ro de wir" = "evacdeserodewir"

                To decrypt the message, we take the ciphertext and the same key
                that was provided for encryption. We then calculate the sequence
                again, but this time in the order that the self.encipher called the
                columns.
                e.g:: ZEBRAS with the encipher sequence of [5, 2, 1, 3, 0, 4]
                      returns the decipher sequence of [4, 2, 1, 3, 5, 0] where
                      each value represents the index value where each letter was
                      stored in the encipher sequence.
                      i.e::
                      decipher_sequence = sorted([
                           (Z, 5) = sequence[0],
                           (E, 2) = sequence[1],
                           (B, 1) = sequence[2],
                           (R, 3) = sequence[3],
                           (A, 0) = sequence[4],
                           (S, 4) = sequence[5],
                      ])
        """

        self.message    = message
        self.keyword    = keyword
        self.encrypt    = encrypt
        self.decrypt    = decrypt
        self.ciphertext = ""
        self.plaintext  = ""

    def __repr__(self):
        if self.encrypt:
            return self.encipher(self.message, self.keyword)
        elif self.decrypt:
            return self.decipher(self.message, self.keyword)

    def encipher(self, plaintext, keyword):
        """
        :param plaintext: message to encrypt
        :param keyword: used to encrypt plaintext. Each char in keyword = new column
        :return: ciphertext string
        """
        message = self.remove_punctuation(plaintext)
        sequence = self.getEncipherKeywordSequence(keyword)
        ciphertext = ""
        for val in range(len(self.keyword)):
            ciphertext += message[sequence.index(val)::len(keyword)]
        # Adding a space every 4 characters to help obfuscate ciphertext
        self.ciphertext = ' '.join([ciphertext[i:i + 4] for i in range(0, len(ciphertext), 4)])
        return self.ciphertext

    def decipher(self, ciphertext, keyword):
        """
        :param ciphertext: encrypted plaintext
        :param keyword: keyword used to encrypt plaintext
        :return: plaintext string
        """
        message = self.remove_punctuation(ciphertext)
        self.plaintext = ['_'] * len(message)
        message_len, keyword_len = len(message), len(keyword)
        decipher_sequence = self.getDecipherKeywordSequence(keyword)
        upto = 0

        for i in range(len(keyword)):
            this_col_len = int(message_len/keyword_len)
            if decipher_sequence[i] < message_len % keyword_len:
                this_col_len += 1
            self.plaintext[decipher_sequence[i]::keyword_len] = message[upto:upto + this_col_len]
            upto += this_col_len
        return ''.join(self.plaintext)

    def getEncipherKeywordSequence(self, keyword):
        '''
            :param keyword: string used to encrypt message
            :return sequence list used to encrypt message
            This function generates the sequence number we will use to
            sort our cipher matrix.

            First, we sort the keyword to get the alphabetical order. Then
            for each character in the keyword, we store the character in a
            character list in order to process any duplicate values.
            Any duplicates found in the char list will be assigned the
            total char count of that char at that point in the loop. Otherwise,
            we append the number current sequence_val (current character value
            in tempSequence).

            Examples:
                keyword "Knowledge" returns sequence list [4, 6, 7, 8, 5, 1, 0, 3, 2]
                'E' appears twice in the string and gets assigned sequence values of
                1 and 2.

                keyword "Aardvark" returns sequence list [0, 1, 5, 3, 7, 2, 6, 4]
                'A' appears 3x and gets assigned sequence values 0, 1, and 2.
        '''
        keyword = keyword.upper()
        sequence = []
        sorted_keyword = sorted(keyword)
        # char_list is used to keep track of visited chars
        char_list = []
        for ch in keyword:
            sequence_val = next((i for i, v in enumerate(sorted_keyword) if v[0] == ch), None)
            if sequence_val in sequence:
                repeat_count = char_list.count(ch)
                sequence.append(repeat_count + sequence_val)
            else:
                sequence.append(int(sequence_val))
            char_list.append(ch)
        print('Enciphered Sequence : %s' % sequence)
        return sequence

    def getDecipherKeywordSequence(self, keyword):
        """
        :param keyword:
        :return: sequence value for the unsorted keyword list. Used to reverse
        the encryption process.

        :Example: ZEBRAS returns sequence list value of [4, 2, 1, 3, 5, 0]
        Where each value is determined by the index position of the
        *unsorted* keyword. Z = keyword[0], E = keyword[1], B = keyword[2], etc.
        """
        keyword = keyword.upper()

        sequence_tuple = [(keyword[i], i) for i in range(len(keyword))]
        sequence = [seq_val[1] for seq_val in sorted(sequence_tuple)]
        print('Deciphered Sequence : %s' % sequence)
        return sequence

    def remove_punctuation(self, message, filter='[^a-zA-Z0-9_=]'):
        """
        :param message: unformatted message.
        :param filter: removes all non-alphanumeric characters except '='
                (In order to preserve Encodings)
        :return: formatted message
        """
        return re.sub(filter, '', message)
