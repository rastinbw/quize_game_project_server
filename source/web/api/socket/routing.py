from django.urls import path
from . import consumers

websocket_urlpatterns = [
	path('api/chat/<slug:room_name>', consumers.ChatConsumer),
]