import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

@database_sync_to_async
def get_app_user_data(user):
    try:
        app_user = AppUser.objects.get(user=user)
        return app_user, app_user.user.username, app_user.profile_image
    except AppUser.DoesNotExist:
        raise StopConsumer

@database_sync_to_async
def create_new_message(sender, chat_room_id, text):
    try:
        chat_room = ChatRoom.objects.get(id=chat_room_id)
        new_message = Message(chat_room=chat_room, sender=sender, text=text)
        new_message.save()
        return new_message.text, new_message.timestamp
    except ChatRoom.DoesNotExist:
        raise StopConsumer

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_room_name = 'chat_%s' % self.chat_id
        await self.channel_layer.group_add(
            self.chat_room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_room_name,
            self.channel_name
        )
        return super().disconnect(close_code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data) 
        message = text_data_json['message']
        chat_room_id = text_data_json['chat_room_id']
        sender, sender_username, profile_image  = await get_app_user_data(user=self.scope['user'])
        text, timestamp = await create_new_message(sender=sender, chat_room_id=chat_room_id, text=message)

        await self.channel_layer.group_send(
            self.chat_room_name,  
            {
                'type' : 'chat_message',
                'message': text,
                'timestamp' : str(timestamp),
                'sender_username': sender_username,
                'profile_image_url' : profile_image.url,
            }
        )

    async def chat_message(self, event):
        sender_username= event['sender_username']
        message = event['message']
        profile_image_url = event['profile_image_url']
        timestamp = event['timestamp']
        await self.send(text_data=json.dumps({ 
            'message': message,
            'sender_username': sender_username,
            'profile_image_url' : profile_image_url,
            'timestamp' : timestamp,
        }))
