import asyncio
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
from web import consts
from web import helpers
from web.models import *
from channels.exceptions import AcceptConnection, DenyConnection, InvalidChannelLayerError, StopConsumer
import json
from asgiref.sync import async_to_sync


class ChatConsumer(AsyncConsumer):
	# async def websocket_connect(self, event):
	# 	print(event)
	groups = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.groups is None:
			self.groups = []

	async def websocket_connect(self, message):
		"""
		Called when a WebSocket connection is opened.
		"""
		await self.send(
			{
				'type': 'websocket.accept'
			}
		)
		'''
				try:
			for group in self.groups:
				await self.channel_layer.group_add(group, self.channel_name)
		except AttributeError:
			raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
		try:
			await self.connect()
		except AcceptConnection:
			await self.accept()
		except DenyConnection:
			await self.close()

	async def close(self, code=None):
		"""
		Closes the WebSocket from the server end
		"""
		if code is not None and code is not True:
			await super().send(
				{"type": "websocket.close", "code": code}
			)
		else:
			await super().send(
				{"type": "websocket.close"}
			)

	async def connect(self):
		# Called on connection.
		# To accept the connection call:
		await self.accept()

	async def accept(self, subprotocol=None):
		"""
		Accepts an incoming socket
		"""
		await super().send({"type": "websocket.accept", "subprotocol": subprotocol})

		'''

	# self.room_name = self.scope['url_route']['kwargs']['room_name']
	# self.room_group_name = 'chat_{}'.format(self.room_name)
	#
	# await self.channel_layer.group_add(
	# 	self.room_group_name,
	# 	self.channel_name,
	# )

	# room_name = self.scope['url_route']['kwargs']['room_name']
	# this_user = self.scope['user']
	# print(room_name, this_user)

	async def websocket_disconnect(self, close_code):
		"""
        Called when a WebSocket connection is closed. Base level so you don't
        need to call super() all the time.
        """

	# Leave room group
	# await self.channel_layer.group_discard(
	# 	self.room_group_name,
	# 	self.channel_name
	# )
	'''
			try:
			for group in self.groups:
				await self.channel_layer.group_discard(group, self.channel_name)
		except AttributeError:
			raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
		await self.disconnect(close_code["code"])
		raise StopConsumer()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.channel_name,
		)
	'''

	async def user_splash_json_update(self, text_data):
		'''
							The Json format that is created by Generator.generate_socket_send_json
				{
					'message': {
								'event': {consts.user_update_info_splash},
								'data': {
											'isTokenValid': True,
											'restrictionInfo': {'isGuest': True, 'unBanDate': None}
										},
								'notifs': {'appUpdate': None,'serverMessage': None}
								}
				}
			'''
		message = text_data['message']
		data = message['data']
		user_name = data['username']
		app_version = data['appVersion']
		# dictioanry = {
		# 	'event': consts.user_update_info_splash,
		# 	'isTokenValid': True,
		# 	'restrictionInfo': None,
		# 	### resteriction info ###
		# 	'isGuest': True,
		# 	'unBanDate': None,
		# 	### notifs ###
		# 	'appUpdate': None,
		# 	'serverMessage': None,
		# }
		await self.send(
			{"type": "websocket.send", "text":
				str(
					helpers.Generator.generate_socket_send_json(
						event=consts.user_update_info_splash,
						isTokenValid=True,
						token=None,
						restrictionInfo=None,
						### resteriction info ###
						isGuest=False,
						unBanDate=None,
						### notifs ###
						appUpdate=None,
						serverMessage=None, )
				)})

	async def onconnect_check(self, event_message):
		'''
		{
			'message': {
				'data': {
					'username': 'alireza',
					'token': '673fe3b39c7346e89ce6d17c18956596'
				}
			}
		}
		'''
		json_object = json.loads(event_message)
		token = json_object['data']['token']
		user_name = json_object['data']['username']
		if not User.objects.filter(username=user_name).exists():
			print("invalid user ...")
			await self.send(
				{
					'type': 'websocket.close'
				}
			)
		if User.objects.filter(username=user_name).exists() and not Token.objects.filter(token=token).exists():
			user = User.objects.get(username=user_name);
			old_token = Token.objects.get(user=user)
			old_token.delete()
			new_token = Token.objects.create(user=user)
			new_token.save()
			await self.send(
				{
					"type": "websocket.send", "text":
					str(
						helpers.Generator.generate_socket_send_json(
							event=consts.user_update_token,
							isTokenValid=False,
							token=str(new_token),
							restrictionInfo=None,
							### resteriction info ###
							isGuest=False,
							unBanDate=None,
							### notifs ###
							appUpdate=None,
							serverMessage=None, )
					)
				}
			)
		if User.objects.filter(username=user_name).exists() and Token.objects.filter(token=token).exists():
			await self.send(
				{
					"type": "websocket.send", "text":
					str(
						helpers.Generator.generate_socket_send_json(
							event=consts.user_update_token,
							isTokenValid=True)
					)
				}
			)

	async def get_or_new_contest(self):
		this_user = User.objects.get(username=self.scope['user'])
		this_user_contestant = Contestant.objects.create(Profile.objects.filter(user=this_user).get())
		contest = Contest.objects.search_opponent(this_user)
		if contest.first_user == this_user_contestant:
			return contest
		else:
			contest.second_user = this_user
			return contest

	# Receive message from WebSocket
	async def websocket_receive(self, text_message):
		text_data_json = json.loads(text_message['text'])
		message = text_data_json['message']
		event = message['event']
		if event == consts.onconnect_check:
			del message['event']
			print('message before dumps: {}'.format(message))
			message = json.dumps(message)
			print('message after dumps: {}'.format(message))
			await self.onconnect_check(message)
		if event == consts.user_update_info_splash:
			await self.user_splash_json_update(text_message)


# # Send message to room group
# await self.channel_layer.group_send(
# 	self.room_group_name,
# 	{
# 		'type': 'chat_message',
# 		'message': message,
# 	}
# )
class TestConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()

	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data=None, bytes_data=None):
		# text_data_json = json.loads(text_data)
		# message = text_data_json['message']
		# message = json.dumps(dict(message=message))
		print('Json object :' + text_data)
		await self.send(text_data)
