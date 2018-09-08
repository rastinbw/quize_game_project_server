import asyncio
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
from web import consts
from web import helpers
from web.models import *


class ChatConsumer(AsyncConsumer):
	async def websocket_connect(self, first_message):
		await self.send(
			{
				'type': 'websocket.accept'
			}
		)

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

	async def disconnect(self, close_code):
		# Leave room group

		# await self.channel_layer.group_discard(
		# 	self.room_group_name,
		# 	self.channel_name
		# )
		pass

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
						restrictionInfo=None,
						### resteriction info ###
						isGuest=True,
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
		print('onconnect event: {} the type is {}'.format(event_message, type(event_message)))
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
			shit = Token.objects.get(user=user)
			shit.delete()
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

	# Receive message from WebSocket
	async def websocket_receive(self, text_message):
		print('JSON: {}'.format(text_message))
		print('JSON string: {}'.format(json.loads(text_message['text'])))
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
