from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import *
from django.dispatch import receiver

class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField('self', blank=True)
    profile_image = models.ImageField(default='default/profile-pic.png', upload_to='profiles/')
    
    def __unicode__(self):
        return self.user.username
    

class Post(models.Model):
    text = models.TextField()
    image = models.ImageField(blank=True, upload_to='posts/')
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=False)

class FriendRequest(models.Model):
    sender = models.ForeignKey(AppUser, related_name='sender',on_delete=models.CASCADE)
    receiver = models.ForeignKey(AppUser, related_name='receiver', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, blank=False)
    pending = models.BooleanField(default=True)


class ChatRoom(models.Model):
    participants = models.ManyToManyField(AppUser, related_name='participants', blank=False)

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='chat_room',on_delete=models.CASCADE)
    text = models.TextField()
    sender = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now_add=True, blank=False)



