from channels.routing import ProtocolTypeRouter, URLRouter
# the ProtoolTypeRouter understands how to route different channel requests to different parts of our app
from channels.auth import AuthMiddlewareStack
# we need the appropriate middleware in order to react to the requests correctly
import tomodachi.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(tomodachi.routing.websocket_urlpatterns)) 
})