import asyncio
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
from web import consts


class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		# self.room_name = self.scope['url_route']['kwargs']['room_name']
		# self.room_group_name = 'chat_{}'.format(self.room_name)
		#
		# await self.channel_layer.group_add(
		# 	self.room_group_name,
		# 	self.channel_name,
		# )
		await self.accept()

	async def disconnect(self, close_code):
		# Leave room group

		# await self.channel_layer.group_discard(
		# 	self.room_group_name,
		# 	self.channel_name
		# )
		pass

	# Receive message from WebSocket
	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		event = message['event']
		data = message['data']
		if event == consts.user_update_info_splash:
			token = data['token']
			user_name = data['username']
			app_version = data['appVersion']
			self.send(
				json.dumps(
					{
						'message': {'event':
										{consts.user_update_info_splash},
									'data': {
										'isTokenValid': True,
										'restrictionInfo': {
											'			isGuest': True, 'unBanDate': None
										}},
									'notifs': {
											'appUpdate': None,
											'serverMessage': None
										}
									}
					}
				)
			)

	# # Send message to room group
	# await self.channel_layer.group_send(
	# 	self.room_group_name,
	# 	{
	# 		'type': 'chat_message',
	# 		'message': message,
	# 	}
	# )

	# Receive message from room group
	async def chat_message(self, event):
		message = event['message']

		# Send message to WebSocket
		await self.send(text_data=json.dumps({
			'message': message,
		}))
