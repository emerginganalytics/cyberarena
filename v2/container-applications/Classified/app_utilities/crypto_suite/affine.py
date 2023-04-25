import string


class Affine:
	def __init__(self, message, key=None, atbash=False):
		self.message = message
		self.alpha = string.ascii_letters
		self.alpha_numeric = string.ascii_letters + string.digits
		self.is_atbash = atbash
		self.output = {'plaintext': '', 'ciphertext': ''}
		self.key = key

	def atbash(self):
		'''
		AtBash is basically a simplified Affine cipher. Here we utilize
		the String library to first make a reversed alphabet which we can use to
		translate the ciphertext to the plaintext with the .translate(DECODE_TABLE)
		call
		'''
		decode_table = str.maketrans(self.alpha, ''.join(reversed(self.alpha)), string.whitespace)
		return str(self.message.translate(decode_table))

	def encrypt(self):
		if self.is_atbash:
			return {'ciphertext': self.atbash(), 'plaintext': self.message, 'key': None}
		else:
			if not self.key:
				raise ValueError('Missing key pair for Affine cipher encrypt method')
			key_1 = self.key['key_1']
			key_2 = self.key['key_2']
			coprime = self.gen_coprime()  # [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
			message = self.message
			alpha_len = len(self.alpha)

			if key_1 not in coprime:
				raise ValueError('key_1 value [%d] is not a coprime of %d!' % (key_1, alpha_len))
			else:
				ciphertext = ''
				for ch in message:
					if ch in self.alpha:
						letter_pos = self.alpha.find(ch)
						letter = self.alpha[(key_1 * letter_pos + key_2) % alpha_len]  # E(x) = (ax + b) % m
						ciphertext += letter
					else:
						ciphertext += ch
				# Set the output object and return
				self.output['ciphertext'] = ciphertext
				self.output['plaintext'] = self.message
				self.output['key'] = self.key
				return self.output

	def decrypt(self):
		"""
		:params key_1
		:params key_2
		:return plaintext

		To decrypt an affine cipher, we take the inverse value of key_1 and multiply it
		to the current character - key_2 before modding it by the alpha_len.
		i.e a^-1(x - b) % 62. If a character is not part of the standard alphabet,
		we simply append that to the plaintext (assuming symbols, punctuation, etc)
		"""
		if self.is_atbash:
			return {'ciphertext': self.message, 'plaintext': self.atbash(), 'key': None}
		else:
			if not self.key:
				raise ValueError('Missing key pair for Affine cipher encrypt method')
			key_1 = self.key['key_1']
			key_2 = self.key['key_2']
			alpha_len = len(self.alpha)
			inv_a = pow(key_1, -1, alpha_len)
			coprime = self.gen_coprime()
			if key_1 not in coprime:
				raise ValueError('key_1 value is not a coprime of %d!' % alpha_len)
			else:
				plaintext = ''
				for ch in self.message:
					if ch in self.alpha:
						letter_pos = self.alpha.find(ch)
						letter = self.alpha[(letter_pos - key_2) * inv_a % alpha_len]
						plaintext += letter
					else:
						plaintext += ch
			self.output = {'plaintext': plaintext, 'ciphertext': self.message, 'key': self.key}
			return self.output

	def gen_coprime(self):
		"""
		:return list of valid numbers for key_1. If key_1 does not exist
		in coprime, we raise a ValueError.
		"""
		coprime = [num for num in range(len(self.alpha)) if num % 2 != 0]
		return coprime
