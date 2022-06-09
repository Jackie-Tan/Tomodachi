from django.contrib.auth.models import User
from . models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class AppUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = AppUser
        fields = ['user', 'profile_image']

class PostSerializer(serializers.ModelSerializer):
    user = AppUserSerializer()
    class Meta:
        model = Post
        fields = ['text', 'timestamp', 'image', 'user', 'id']

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = AppUserSerializer()
    receiver = AppUserSerializer()
    class Meta:
        model = FriendRequest
        fields = ['id' , 'timestamp', 'sender', 'receiver']






