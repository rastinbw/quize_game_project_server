import asyncio
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json


class ChatConsumer(AsyncConsumer):
	async def websocket_connect(self, event):
		print("connected", event)
		await self.send(
			{
				"type": "websocket.accept"
			}
		)

		# await asyncio.sleep(10)
		await self.send({
			"type": "websocket.send",
			"message": "hello world"
		})

	async def websocket_receive(self, event):
		print("receive", event)

	async def websocket_disconnect(self, event):
		print("disconnected", event)




	'''
class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):

		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = 'chat_{}'.format(self.room_name)

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name,
		)
		await self.accept()

	async def disconnect(self, close_code):
		# Leave room group
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

	# Receive message from WebSocket
	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']

		# Send message to room group
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'chat_message',
				'message': message,
			}
		)

	# Receive message from room group
	async def chat_message(self, event):
		message = event['message']

		# Send message to WebSocket
		await self.send(text_data=json.dumps({
			'message': message,
		}))




	'''
