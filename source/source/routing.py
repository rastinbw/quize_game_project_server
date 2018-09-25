from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from channels.auth import AuthMiddlewareStack
import web.api.socket.routing
from django.urls import path
from web.api.socket import consumers
from web.helpers import QueryAuthMiddleware

application = ProtocolTypeRouter({
	'websocket': QueryAuthMiddleware(
			URLRouter(
				web.api.socket.routing.websocket_urlpatterns,
			)
		)
})
