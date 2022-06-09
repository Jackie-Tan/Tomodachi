from .. model_factories import *
from .. models import *
from .. routing import websocket_urlpatterns
from channels.testing import WebsocketCommunicator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.test import TransactionTestCase, TestCase
from .. consumers import get_app_user_data, create_new_message

class ChatConsumerTest(TransactionTestCase):

    sender = None
    receiver = None
    django_asgi_app = None
    application = None
    chat_room = None

    def setUp(self):
        self.application = ProtocolTypeRouter({
            "websocket": AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            ),
        })
        self.sender = AppUserFactory.create()
        self.receiver = AppUserFactory.create()
        self.chat_room = ChatRoomFactory.create(participants=[self.sender, self.receiver])
        self.client.force_login(user=self.sender.user)
        return super().setUp()

    def tearDown(self):
        Message.objects.all().delete()
        MessageFactory.reset_sequence()
        ChatRoom.objects.all().delete()
        ChatRoomFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    async def test_ChatConsumer(self):
        communicator = WebsocketCommunicator(self.application, "/ws/" + str(self.chat_room.id) + "/")
        communicator.scope["user"] = self.sender.user
        connected, subprotocol = await communicator.connect()   
        self.assertTrue(connected)
        chat_dict = {"chat_room_id": str(self.chat_room.id), "message": "hi", "target_username" : self.sender.user.username}
        await communicator.send_json_to(chat_dict)
        response = await communicator.receive_json_from()
        self.assertEqual(response['message'], chat_dict['message'])
        self.assertEqual(response['sender_username'], self.sender.user.username)

class ChatConsumerMethodTests(TestCase):

    def setUp(self):
        self.sender = AppUserFactory.create()
        self.receiver = AppUserFactory.create()
        self.chat_room = ChatRoomFactory.create(participants=[self.sender, self.receiver])
        self.client.force_login(user=self.sender.user)
        return super().setUp()

    def tearDown(self):
        Message.objects.all().delete()
        MessageFactory.reset_sequence()
        ChatRoom.objects.all().delete()
        ChatRoomFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    async def test_GetAppUserReturnCorrectData(self):
        app_user, username, profile_image = await get_app_user_data(self.sender.user)
        self.assertEqual(self.sender, app_user)
        self.assertEqual(self.sender.user.username, username)

    async def test_NewMessageReturnsCorrectData(self):
        message = 'message'
        text, timestamp = await create_new_message(self.sender, self.chat_room.id, message)
        self.assertEqual(message, text)
