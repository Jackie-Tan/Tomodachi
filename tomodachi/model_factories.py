import datetime
from .models import *
from django.contrib.auth.models import User
import factory
from django.conf import settings

class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    class Meta:
        model = User

class AppUserFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    profile_image = factory.django.ImageField()
    class Meta:
        model = AppUser

    @factory.post_generation
    def friends(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for friend in extracted:
                self.friends.add(friend)
    

class PostFactory(factory.django.DjangoModelFactory):
    text = factory.Faker('text')
    user = factory.SubFactory(AppUserFactory)
    image = factory.django.ImageField()
    timestamp = datetime.datetime.now().time()
    class Meta:
        model = Post

class FriendRequestFactory(factory.django.DjangoModelFactory):
    sender = factory.SubFactory(AppUserFactory)
    receiver = factory.SubFactory(AppUserFactory)
    timestamp = datetime.datetime.now().time()
    pending = True
    class Meta:
        model = FriendRequest

class ChatRoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatRoom
    
    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for app_user in extracted:
                self.participants.add(app_user)

class MessageFactory(factory.django.DjangoModelFactory):
    chat_room = factory.SubFactory(ChatRoomFactory)
    text = factory.Faker('text')
    sender = factory.SubFactory(AppUserFactory)
    timestamp = datetime.datetime.now().time()
    class Meta:
        model = Message


