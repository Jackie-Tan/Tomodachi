from django.test import TestCase
from .. serializers import *
from .. model_factories import *

class UserSerializerTest(TestCase):
    user = None
    serializer = None

    def setUp(self):
        self.user = UserFactory.create()
        self.serializer = UserSerializer(instance=self.user)
        return super().setUp()
    
    def tearDown(self):
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_UserSerializerReturnCorrectKeys(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['username']))

    def test_UserSerializerReturnCorrectData(self):
        data = self.serializer.data
        for key in data.keys():
            self.assertEqual(data[key], self.user.__dict__[key])

class AppUserSerializerTest(TestCase):
    app_user = None
    serializer = None

    def setUp(self):
        self.app_user = AppUserFactory.create(friends=AppUserFactory.create_batch(size=2))
        self.serializer = AppUserSerializer(instance=self.app_user)
        return super().setUp()

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()
    
    def test_AppUserSerializerReturnCorrectKeys(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['user', 'profile_image']))
    
    def test_AppUserSerializerReturnCorrectData(self):
        data = self.serializer.data
        self.assertEqual(data['user']['username'], self.app_user.user.username)

class PostSerializerTest(TestCase):
    post = None
    serializer = None

    def setUp(self):
        self.post = PostFactory.create()
        self.serializer = PostSerializer(instance=self.post)
        return super().setUp()

    def tearDown(self):
        Post.objects.all().delete()
        PostFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()
    
    def test_PostSerializerReturnCorrectKeys(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set( ['text', 'timestamp', 'image', 'user', 'id']))

    def test_PostSerializerReturnCorrrectData(self):
        data = self.serializer.data
        self.assertEqual(data['text'], self.post.text)
        self.assertEqual(data['user']['user']['username'], self.post.user.user.username)
        self.assertEqual(data['id'], self.post.id)
        self.assertEqual(datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), self.post.timestamp.replace(tzinfo=None))
    
class FriendRequestSerializerTest(TestCase):
    friend_request = None
    serializer = None

    def setUp(self):
        self.friend_request = FriendRequestFactory.create()
        self.serializer = FriendRequestSerializer(instance=self.friend_request)
        return super().setUp()

    def tearDown(self):
        FriendRequestFactory.reset_sequence()
        FriendRequest.objects.all().delete()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_FriendRequestSerializerReturnCorrectKeys(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id' , 'timestamp', 'sender', 'receiver']))

    def test_FriendRequestSerializerReturnCorrectData(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.friend_request.id)
        self.assertEqual(datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), self.friend_request.timestamp.replace(tzinfo=None))
        self.assertEqual(data['sender']['user']['username'], self.friend_request.sender.user.username)
        self.assertEqual(data['receiver']['user']['username'], self.friend_request.receiver.user.username)