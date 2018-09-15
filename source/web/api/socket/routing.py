from django.urls import path
from . import consumers
from web.helpers import Generator

websocket_urlpatterns = [
	# path('api/chat/<slug:room_name>', consumers.ChatConsumer),
	path('api/chat/<slug:room_name>', consumers.ChatConsumer),
	path('api/chat/test/echo', consumers.TestConsumer),
]