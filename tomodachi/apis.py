import json
from django.http import HttpResponse
from . models import *
from . serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class RetrieveFeedPosts(generics.ListAPIView):
    description = 'Gets a list of posts from who you are following'
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        app_user = AppUser.objects.get(user=self.request.user)
        self.queryset = Post.objects.filter(user__in=app_user.friends.all()).order_by('-timestamp')
        return super().get_queryset()

    def handle_exception(self, exception):
        if exception and (type(exception) == AppUser.DoesNotExist):
            return Response(status=404)
        return super().handle_exception(exception)

class RetrievePendingFriendRequests(generics.ListAPIView):
    description = 'Gets a list of pending friend requests of a given username'
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        app_user = AppUser.objects.get(user=self.request.user)
        self.queryset = FriendRequest.objects.filter(receiver=app_user, pending=True).order_by('-timestamp')
        return super().get_queryset()

    def handle_exception(self, exception):
        if exception and (type(exception) == AppUser.DoesNotExist):
            return Response(status=404)
        return super().handle_exception(exception)

class RetrieveAllPosts(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all().order_by('-timestamp')
    description = 'Get all the posts'

class CreatePost(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class RetrievePost(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    description = 'Gets a post based on a provided post id'
        
class RetrieveUserPosts(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    description = 'Gets a list of posts created by the user'

    def get_queryset(self):
        username = self.kwargs['username']
        self.queryset = Post.objects.filter(user__user__username=username).order_by('-timestamp')
        return super().get_queryset()

class RetrieveAppUserFriends(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppUserSerializer
    description = 'Get all friends of the requested user'

    def get_queryset(self):
        username = self.kwargs['username']
        requested_user = AppUser.objects.get(user__username=username)
        self.queryset = AppUser.objects.filter(friends__exact=requested_user)
        return super().get_queryset()

    def handle_exception(self, exception):
        if exception and (type(exception) == AppUser.DoesNotExist):
            return Response(status=404)
        return super().handle_exception(exception)

class RetrieveAppUserDetails(APIView):
    permission_classes = [IsAuthenticated]
    description = 'Get all we can know about the user'

    def get(self, request, username, format=None):
        requested_user = AppUser.objects.get(user__username=username)
        requested_user_posts = Post.objects.filter(user=requested_user)

        requested_user_friends = requested_user.friends

        response = AppUserSerializer(requested_user).data
        response['friends'] = AppUserSerializer(requested_user_friends, many=True).data
        response['posts'] = PostSerializer(requested_user_posts, many=True).data
        return Response(response)
        
    def handle_exception(self, exception):
        if exception and (type(exception) == AppUser.DoesNotExist):
            return Response(status=404)
        return super().handle_exception(exception)