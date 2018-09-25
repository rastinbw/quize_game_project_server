# coding: utf-8
from __future__ import unicode_literals
from django.http import HttpResponse
from django.conf import settings
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from uuid import uuid4
import base64
import six
import json
import os
from random import randint
from web import consts
from web import models
from django.contrib.auth.models import User
from django.db import close_old_connections


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "source.settings")


class PublicKeyFileExists(Exception):
	pass


class JsonResponse(HttpResponse):
	def __init__(self, content, status=200):
		super().__init__(content, status=status, content_type="application/json")


class AESEncryption(object):
	_BLOCK_SIZE = 16

	def __init__(self, key, iv):
		self._key = key
		self._iv = iv

	# Encryption using AES CBC (128-bits) with PKCS5padding
	def encrypt(self, plain_text):
		aes = AES.new(self._key, AES.MODE_CBC, self._iv)
		return base64.b64encode(aes.encrypt(self.pad(plain_text)))

	# Decryption using AES CBC (128-bits) with PKCS5padding
	def decrypt(self, cipher_text):
		decrypted = base64.b64decode(cipher_text)
		aes = AES.new(self._key, AES.MODE_CBC, self._iv)
		plaintext = self.un_pad(aes.decrypt(decrypted)).decode('utf-8')
		return plaintext

	def pad(self, s):
		return s + (self._BLOCK_SIZE - len(s) % self._BLOCK_SIZE) * \
			   chr(self._BLOCK_SIZE - len(s) % self._BLOCK_SIZE)

	@staticmethod
	def un_pad(s):
		return s[:-ord(s[len(s) - 1:])]


class RSAEncryption(object):
	PUBLIC_KEY_FILE_PATH = settings.RSA_DIR + '/rsa.pub'
	PRIVATE_KEY_FILE_PATH = settings.RSA_DIR + '/rsa.pv'

	def encrypt(self, message):
		public_key = self._get_public_key()
		public_key_object = RSA.importKey(public_key)
		random_phrase = 'R'
		encrypted_message = public_key_object.encrypt(self._to_format_for_encrypt(message), random_phrase)[0]
		# use base64 for save encrypted_message in database without problems with encoding
		return base64.b64encode(encrypted_message)

	def decrypt(self, encoded_encrypted_message):
		encrypted_message = base64.b64decode(encoded_encrypted_message)
		private_key = self._get_private_key()
		private_key_object = RSA.importKey(private_key)
		decrypted_message = private_key_object.decrypt(encrypted_message)
		return decrypted_message

	def generate_keys(self):
		"""Be careful rewrite your keys"""
		random_generator = Random.new().read
		key = RSA.generate(1024, random_generator)
		private, public = key.exportKey(), key.publickey().exportKey()

		if os.path.isfile(self.PUBLIC_KEY_FILE_PATH):
			raise PublicKeyFileExists('There is no public key in directory.')
		self.create_directories()

		with open(self.PRIVATE_KEY_FILE_PATH, 'wb') as private_file:
			private_file.write(private)
		with open(self.PUBLIC_KEY_FILE_PATH, 'wb') as public_file:
			public_file.write(public)
		return private, public

	def create_directories(self, for_private_key=True):
		public_key_path = self.PUBLIC_KEY_FILE_PATH.rsplit('/', 1)[0]
		if not os.path.exists(public_key_path):
			os.makedirs(public_key_path)
		if for_private_key:
			private_key_path = self.PRIVATE_KEY_FILE_PATH.rsplit('/', 1)[0]
			if not os.path.exists(private_key_path):
				os.makedirs(private_key_path)

	def _get_public_key(self):
		"""run generate_keys() before get keys """
		with open(self.PUBLIC_KEY_FILE_PATH, 'rb') as _file:
			return _file.read()

	def _get_private_key(self):
		"""run generate_keys() before get keys """
		with open(self.PRIVATE_KEY_FILE_PATH, 'rb') as _file:
			return _file.read()

	@staticmethod
	def _to_format_for_encrypt(value):
		if isinstance(value, int):
			return six.binary_type(value)
		for str_type in six.string_types:
			if isinstance(value, str_type):
				return value.encode('utf8')
		if isinstance(value, six.binary_type):
			return value


class Generator(object):
	@staticmethod
	def generate_uuid(model,
					  field,
					  prefix='',
					  gen_function=lambda: uuid4().hex):

		uuid_found = False
		while not uuid_found:
			uuid = gen_function()
			# This weird looking construction is a way to pass a value to a field with a dynamic name
			if model.objects.filter(**{field: uuid}).count() is 0:
				uuid_found = True
		return prefix + uuid

	@staticmethod
	def generate_result(message="", result_code=1000, key=None):
		encoder = json.JSONEncoder()

		if key is not None and key is not "":
			key, iv = Generator.get_key_and_iv(key)
			aes = AESEncryption(key=key, iv=iv)
			enc_message = aes.encrypt(encoder.encode(message))
			result = {'is_encrypted': True,
					  'result_code': result_code,
					  'message': str(enc_message)}
		else:
			result = {'is_encrypted': False,
					  'result_code': result_code,
					  'message': message}

		return encoder.encode(result)

	@staticmethod
	def get_key_and_iv(key_and_iv):
		rsa = RSAEncryption()
		drd = rsa.decrypt(encoded_encrypted_message=key_and_iv)

		return drd[:16], drd[16:]

	@staticmethod
	def generate_dict_from_enc(enc, key):
		key, iv = Generator.get_key_and_iv(key)
		aes = AESEncryption(key=key, iv=iv)
		obj = aes.decrypt(enc)
		print(json.loads(obj))
		return json.loads(obj)

	@staticmethod
	def generate_event_for_json(event=None):
		key = ["event"]
		result_event = dict.fromkeys(key)
		result_event["event"] = event
		return result_event

	@staticmethod
	def generate_data_for_restriction_info(isGuest=False, unBanDate=None):
		keys = ["isGuest", "unBanDate"]
		restriction_info = dict.fromkeys(keys)
		restriction_info["isGuest"] = isGuest
		restriction_info["unBanDate"] = unBanDate
		print("restriction is gerating ...{}".format(restriction_info))
		return restriction_info

	@staticmethod
	def generate_data_for_json(restriction_info, isTokenValid=False, token=None):
		restriction_info = Generator.generate_data_for_restriction_info()
		keys = ["isTokenValid", "restriction_info", "token"]
		data = dict.fromkeys(keys)
		print("generated dic --> {}".format(data))
		data['isTokenValid'] = isTokenValid
		data['restriction_info'] = restriction_info
		data['token'] = token
		print("data is generating ... {}".format(data))
		return data

	@staticmethod
	def generate_notifs_for_json(appUpdate=None, serverMessage=None):
		keys = ["appUpdate", "serverMessage"]
		notifs = dict.fromkeys(keys)
		notifs["appUpdate"] = appUpdate
		notifs["serverMessage"] = serverMessage
		print("notifs is generating ... {}".format(notifs))
		return notifs

	@staticmethod
	def generate_socket_send_json(**kwargs):
		print('hello')
		print('kwargs is : {}'.format(kwargs))
		print('the event is {} and the isTokenValid is {} and the restrictionInfo is {}'.format(
			kwargs.get('event'), kwargs.get('isTokenValid'), kwargs.get('restrictionInfo')))
		event = Generator.generate_event_for_json(kwargs.get("event"))
		data = Generator.generate_data_for_json(kwargs.get("restrictionInfo"), kwargs.get("isTokenValid"),
												kwargs.get("token"))
		notifs = Generator.generate_notifs_for_json(kwargs.get("appUpdate"), kwargs.get("serverMessage"))

		message = dict(message={**event,
								'data': data,
								'notifs': notifs})
		result_encoder = json.JSONEncoder()
		result_encoder = result_encoder.encode(message)
		print('the result encoded JSON: {}'.format(result_encoder))
		return result_encoder

# TODO build a cid generator and add it as the route for the user
# it must be combinition of user + uuid(16bit)


class QueryAuthMiddleware:
	"""
	Custom middleware (insecure) that takes user IDs from the query string.
	"""

	def __init__(self, inner):
		# Store the ASGI application we were passed
		self.inner = inner

	def __call__(self, scope):
		# Look up user from query string (you should also do things like
		# check it's a valid user ID, or if scope["user"] is already populated)
		# id = scope['url_route']['kwargs']['room_name']
		print(scope['query_string'])
		username = str(scope['query_string']).split('=')[1].replace('\'', '')
		user = User.objects.get(username=username)
		close_old_connections()
		# Return the inner application directly and let it run everything else
		return self.inner(dict(scope, user=user))
