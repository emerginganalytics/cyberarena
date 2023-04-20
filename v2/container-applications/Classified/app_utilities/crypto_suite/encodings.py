import base64
from app_utilities.globals import CipherModes


class Encodings:
	"""
	:arg: @mode Either 0 or 1 (Encode or Decode)
	arg: @message if Mode=0, message is plaintext else message is 'ciphertext'
	:returns: plaintext or encoded text based on Mode value
	"""
	def __init__(self, mode, message):
		self.message = message
		self.mode = mode
		self.plaintext = ''

	def base32(self):
		if self.mode == CipherModes.ENCRYPT:
			pass
		elif self.mode == CipherModes.DECRYPT:
			try:
				self.plaintext = str(base64.b32decode(self.message).decode('UTF-8'))
			except ValueError:
				return "Invalid Chars: String is not a Base32 Decodable String ..."
			return {'plaintext': str(self.plaintext), 'key': None, 'ciphertext': self.message}

	def base64(self):
		if self.mode == CipherModes.ENCRYPT:
			pass
		elif self.mode == CipherModes.DECRYPT:
			try:
				self.plaintext = str(base64.b64decode(self.message).decode('UTF-8'))
			except ValueError:
				return "Invalid Chars: String is not a Base64 Decodable String..."
			return {'plaintext': str(self.plaintext), 'key': None, 'ciphertext': self.message}
