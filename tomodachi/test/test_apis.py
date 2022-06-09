import json
from .. model_factories import *
from .. serializers import *
from .. models import *
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse

class RetrieveUserAPITest(APITestCase):
    app_user = None
    posts = []
    app_user_friends = []
    valid_url_and_params = ''
    invalid_url_and_params = ''

    def setUp(self):
        self.app_user_friends = AppUserFactory.create_batch(size=2)
        self.app_user = AppUserFactory.create(friends=self.app_user_friends)
        self.posts = PostFactory.create_batch(size=2, user=self.app_user)
        self.valid_url_and_params = reverse('user_api', kwargs={'username': self.app_user.user.username})
        self.invalid_url_and_params = reverse('user_api', kwargs={'username': 'XXXXXX'})
        return super().setUp()
    
    def tearDown(self):
        Post.objects.all().delete()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        PostFactory.reset_sequence()
        return super().tearDown()
    
    def test_RetrieveUserAPIReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        self.assertEqual(response.status_code, 200)

    def test_RetrieveUserAPIReturnFailureStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.invalid_url_and_params, format='json')
        self.assertEqual(response.status_code, 404)

    def test_RetrieveUserAPIAuthentication(self):
        response = self.client.get(self.valid_url_and_params, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_RetrieveUserAPIReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual(set(data.keys()), set(['user', 'profile_image', 'friends', 'posts']))
        if data['user']:
            self.assertEqual(set(data['user'].keys()), set(['username']))
        if data['posts']:
            for post in data['posts']:
                self.assertEqual(set(post.keys()), set(['user', 'image', 'text', 'timestamp', 'id']))
    
    def test_RetrieveUserAPIReturnCorrectData(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual(len(data['posts']), len(self.posts))
        self.assertEqual(len(data['friends']), len(self.app_user_friends))
        if data['posts']:
            for post in data['posts']:
                for created_post in self.posts:
                    if (post['id'] == created_post):
                        self.assertEqual(post['text'], created_post.text)
                        self.assertEqual(post['user']['username', created_post.user.username])
                        self.assertEqual(datetime.datetime.strptime(post['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), created_post.timestamp.replace(tzinfo=None))
        if data['friends']:
            count_correct_friend_data = 0
            for user in data['friends']:
                for created_user in self.app_user_friends:
                    if (user['user']['username'] == created_user.user.username):
                        count_correct_friend_data += 1
            self.assertEqual(count_correct_friend_data, len(self.app_user_friends))
                    
class RetrievePostAPITest(APITestCase):
    app_user = None
    post = None
    valid_url_and_params = ''
    invalid_url_and_params = ''

    def setUp(self):
        self.app_user = AppUserFactory.create()
        self.post = PostFactory.create()
        self.valid_url_and_params = reverse('post_api',  kwargs={'id': str(self.post.id)}) 
        self.invalid_url_and_params = reverse('post_api',  kwargs={'id': '0'})
        return super().setUp()
    
    def tearDown(self):
        Post.objects.all().delete()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        PostFactory.reset_sequence()
        return super().tearDown()
    
    def test_RetrievePostAPIReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        self.assertEqual(response.status_code, 200)

    def test_RetrievePostAIReturnNotFoundErrorCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.invalid_url_and_params, format='json')
        self.assertEqual(response.status_code, 404)
    
    def test_RetrievePostAPIAuthentication(self):
        response = self.client.get(self.invalid_url_and_params, format='json')
        self.assertEqual(response.status_code, 403)

    def test_RetrievePostAPIReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual(set(data.keys()), set(['text', 'timestamp', 'image', 'user', 'id']))

    def test_RetrievePostAPIReturnCorrectData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual(data['text'], self.post.text)
        self.assertEqual(data['user']['user']['username'], self.post.user.user.username)
        self.assertEqual(data['id'], self.post.id)
        self.assertEqual(datetime.datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), self.post.timestamp.replace(tzinfo=None))

class ExploreAPITest(APITestCase):
    app_user = None
    posts = []
    valid_url = ''

    def setUp(self):
        self.app_user = AppUserFactory.create()
        self.posts = PostFactory.create_batch(size=2)
        self.valid_url = reverse('explore_api')
        return super().setUp()
    
    def tearDown(self):
        Post.objects.all().delete()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        PostFactory.reset_sequence()
        return super().tearDown()

    def test_ExploreAPIReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 200)
    
    def test_ExploreAPIAuthentication(self):
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_ExploreAPIReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for post in data:
            self.assertEqual(set(post.keys()), set(['text', 'timestamp', 'image', 'user', 'id']))
    
    def test_ExploreAPIReturnCorrectDataCount(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        self.assertEqual(len(self.posts), len(data))

    def test_ExploreAPIReturnCorrectData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for post in data:
            for created_post in self.posts:
                if (post['id'] == created_post):
                    self.assertEqual(post['text'], created_post.text)
                    self.assertEqual(post['user']['username', created_post.user.username])
                    self.assertEqual(datetime.datetime.strptime(post['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), created_post.timestamp.replace(tzinfo=None))

class RetrieveUserPostsAPITest(APITestCase):
    app_user = None
    posts = []
    valid_url_and_params = ''
    invalid_url_and_params = ''

    def setUp(self):
        self.app_user = AppUserFactory.create()
        self.posts = PostFactory.create_batch(size=5, user=self.app_user)
        self.valid_url_and_params = reverse('user_posts_api', kwargs={'username': self.app_user.user.username})
        self.invalid_url_and_params = reverse('user_posts_api', kwargs={'username': 'XXXXXX'})
        return super().setUp()
    
    def tearDown(self):
        Post.objects.all().delete()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        PostFactory.reset_sequence()
        return super().tearDown()
    
    def test_RetrieveUserPostsAPIReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        self.assertEqual(response.status_code, 200)

    def test_RetrieveUserPostsAPIAuthentication(self):
        response = self.client.get(self.valid_url_and_params, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_RetrieveUserPostsAPIReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        for post in data:
            self.assertEqual(set(post.keys()), set(['text', 'timestamp', 'image', 'user', 'id']))
    
    def test_RetrieveUserPostsAPIReturnCorrectDataCount(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual(len(self.posts), len(data))
        response = self.client.get(self.invalid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual(0, len(data))

    def test_RetrieveUserPostsAPIReturnCorrectData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url_and_params, format='json')
        data = json.loads(response.content)
        for post in data:
            for created_post in self.posts:
                if (post['id'] == created_post):
                    self.assertEqual(post['text'], created_post.text)
                    self.assertEqual(post['user']['username', created_post.user.username])
                    self.assertEqual(datetime.datetime.strptime(post['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), created_post.timestamp.replace(tzinfo=None))
        response = self.client.get(self.invalid_url_and_params, format='json')
        data = json.loads(response.content)
        self.assertEqual([], data)


class RetrieveUserFriendsAPITest(APITestCase):
    app_user = None
    app_user_friends = []
    valid_url = ''
    invalid_url_and_params = ''

    def setUp(self):
        self.app_user_friends = AppUserFactory.create_batch(size=3)
        self.app_user = AppUserFactory.create(friends=self.app_user_friends)
        self.valid_url = reverse('user_friends_api', kwargs={'username': self.app_user.user.username})
        self.invalid_url_and_params = reverse('user_friends_api', kwargs={'username': 'XXXXXX'})
        return super().setUp()
    
    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        return super().tearDown()
    
    def test_RetrieveUserFriendsAPIReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 200)    

    def test_RetrieveUserFriendsAPIReturnFailureStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.invalid_url_and_params, format='json')
        self.assertEqual(response.status_code, 404)    

    def test_RetrieveUserFriendsAPIAuthentication(self):
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_RetrieveUserFriendsAPIReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for user in data:
            self.assertEqual(set(user.keys()), set(['user', 'profile_image']))
    
    def test_RetrieveUserFriendsAPIReturnCorrectDataCount(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        self.assertEqual(len(self.app_user.friends.all()), len(data))
    

class RetrieveUserFeedPostsAPITest(APITestCase):
    app_user = None
    app_user_friends = []
    posts = set()
    valid_url = ''

    def setUp(self):
        self.app_user_friends = AppUserFactory.create_batch(size=3)
        self.app_user = AppUserFactory.create(friends=self.app_user_friends)
        for friend in self.app_user_friends:
            self.posts.add(PostFactory.create(user=friend))
        self.valid_url = reverse('feed_api')
        return super().setUp()
    
    def tearDown(self):
        Post.objects.all().delete()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        PostFactory.reset_sequence()
        return super().tearDown()
    
    def test_RetrieveUserFeedPostsAPITestReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 200)    

    def test_RetrieveUserFeedPostsAPITestAuthentication(self):
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_RetrieveUserFeedPostsAPIReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for post in data:
            self.assertEqual(set(post.keys()), set(['text', 'timestamp', 'image', 'user', 'id']))
            if post['user']:
                self.assertEqual(set(post['user'].keys()), set(['user', 'profile_image']))
            if post['user']['user']:
                self.assertEqual(set(post['user']['user'].keys()), set(['username']))
    
    def test_RetrieveUserFeedPostsAPIReturnCorrectDataCount(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        self.assertEqual(len(self.posts), len(data))

    def test_RetrieveUserFeedPostsAPIReturnCorrectData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for post in data:
            for created_post in self.posts:
                if (post['id'] == created_post):
                    self.assertEqual(post['text'], created_post.text)
                    self.assertEqual(post['user']['username', created_post.user.username])
                    self.assertEqual(datetime.datetime.strptime(post['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), created_post.timestamp.replace(tzinfo=None))

class RetrievePendingFriendRequestsAPITest(APITestCase):
    app_user = None
    other_app_users = []
    user_friend_requests = []
    valid_url = ''

    def setUp(self):
        self.other_app_users = AppUserFactory.create_batch(size=2)
        self.app_user = AppUserFactory.create()

        friend_requests = []
        for other_user in self.other_app_users:
            friend_requests.append(FriendRequestFactory.create(sender=other_user, receiver=self.app_user))
        self.user_friend_requests = friend_requests
        self.valid_url = reverse('pending_friend_requests_api')
        return super().setUp()
    
    def tearDown(self):
        FriendRequest.objects.all().delete()
        FriendRequestFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        return super().tearDown()
    
    def test_RetrievePendingFriendRequestsAPITestReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 200)    

    def test_RetrievePendingFriendRequestsAPITestAuthentication(self):
        response = self.client.get(self.valid_url, format='json')
        self.assertEqual(response.status_code, 403)
    
    def test_RetrievePendingFriendRequestsAPITestReturnCorrectKeys(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for request in data:
            self.assertEqual(set(request.keys()), set(['id', 'timestamp', 'sender', 'receiver']))
            if request['sender']:
                self.assertEqual(set(request['sender'].keys()), set(['user', 'profile_image']))
            if request['sender']['user']:
                self.assertEqual(set(request['sender']['user'].keys()), set(['username']))
    
    def test_RetrievePendingFriendRequestsAPITestReturnCorrectDataCount(self): 
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        self.assertEqual(len(self.user_friend_requests), len(data))

    def test_RetrievePendingFriendRequestsAPITestReturnCorrectData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url, format='json')
        data = json.loads(response.content)
        for request in data:
            for created_request in self.user_friend_requests:
                if(request['id'] == created_request.id):
                    self.assertEqual(request['sender']['user']['username'], created_request.sender.user.username)
                    self.assertEqual(request['receiver']['user']['username'], created_request.receiver.user.username)
                    self.assertEqual(datetime.datetime.strptime(request['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), created_request.timestamp.replace(tzinfo=None))
                    