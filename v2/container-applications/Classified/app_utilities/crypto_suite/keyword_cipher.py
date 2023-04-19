import string


class KeywordCipher:
	def __init__(self, message, key):
		self.message = message
		self.key = key

	def encrypt(self):
		pass

	def decrypt(self):
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
		for ch in self.key.upper():
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
		plaintext = ''
		for letter in message:
			if letter == " " or letter == '{' or letter == '}':
				plaintext += letter
			else:
				for item in alpha_key:
					if letter in item[1]:
						plaintext += item[0]
		return {'plaintext': plaintext, 'ciphertext': self.message, 'key': self.key}
