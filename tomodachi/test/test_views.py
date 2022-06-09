import json
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .. forms import *
from .. model_factories import *
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os

class LoginViewTest(APITestCase):

    valid_url = ''
    user = None
    app_user = None
    password = 'password'

    def setUp(self):
        self.client.logout()
        self.user = UserFactory.create(password=self.password)
        self.app_user = AppUserFactory.create(user=self.user)
        self.valid_url = reverse('login')
        return super().setUp()

    def tearDown(self):
        UserFactory.reset_sequence()
        AppUserFactory.reset_sequence()
        AppUser.objects.all().delete()
        User.objects.all().delete()
        return super().tearDown()

    def test_LoginViewTestReturnSuccessStatusCode(self):
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)

    def test_LoginViewReturnCorrectContext(self):
        response = self.client.get(self.valid_url)
        form = response.context['form']
        self.assertIsInstance(form, AuthenticationForm)

    def test_LoginViewReturnCorrectTemplate(self):
        response = self.client.get(self.valid_url)
        templates = response.templates
        template_names = [template.name for template in templates]
        self.assertIn('login.html', template_names)

class TestLogoutViewTest(APITestCase):

    valid_url = ''

    def setUp(self):
        self.client.force_login(user=UserFactory.create())
        self.valid_url = reverse('logout')
        return super().setUp()

    def tearDown(self):
        AppUserFactory.reset_sequence()
        AppUser.objects.all().delete()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_LogoutRedirects(self):
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 302)

class IndexViewTest(APITestCase):

    app_user = None
    valid_url = ''
    post_form = None

    def setUp(self):
        self.app_user = AppUserFactory()
        self.valid_url = reverse('index')
        self.post_form = PostForm
        return super().setUp()
    
    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()
    
    def test_IndexViewReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)

    def test_IndexViewRedirects(self):
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 302)

    def test_IndexViewReturnCorrectContext(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url)
        app_user_from_context = response.context['app_user']
        if app_user_from_context:
            app_user_from_context = self.app_user

        post_form_from_context = response.context['post_form']
        if post_form_from_context:
            self.assertEqual(type(post_form_from_context), self.post_form)

class SignUpViewTest(APITestCase):
    app_user = None
    valid_url = ''

    def setUp(self):
        self.app_user = AppUserFactory()
        self.valid_url = reverse('sign_up')
        return super().setUp() 
    
    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_SignUpViewTestReturnSuccessStatusCode(self):
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)

    def test_SignUpViewTestReturnRedirectSuccessfully(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url)
        self.assertRedirects(response, expected_url='/', status_code=302, target_status_code=200)
    
    def test_SignUpViewReturnCorrectContext(self):
        response = self.client.get(self.valid_url)
        form_from_context = response.context['form']
        self.assertIsInstance(form_from_context, UserCreationForm)
    
    def test_SignUpViewReturnFormErrorWhenUsernameNotProvided(self):
        response = self.client.post(self.valid_url, data={'password1': 'RandomPassword', 'password2': 'RandomPassword'})
        self.assertFormError(response=response, form='form', errors='This field is required.',field='username')
        
    def test_SignUpViewReturnFormErrorWhenPasswordsNotProvided(self):
        response = self.client.post(self.valid_url, data={'username': 'RandomUsername', 'password1': 'RandomPassword'})
        self.assertFormError(response=response, form='form', errors='This field is required.',field='password2')
        response = self.client.post(self.valid_url, data={'username': 'RandomUsername', 'password2': 'RandomPassword'})
        self.assertFormError(response=response, form='form', errors='This field is required.',field='password1')

class SearchFriendViewTest(APITestCase):
    app_user = None
    valid_url = ''
    search_term = 'test'
    existing_users = []

    def setUp(self):
        self.search_term = 'test'
        self.app_user = AppUserFactory()
        existing_user1 = AppUserFactory.create(user=UserFactory(username='tester1'))
        existing_user2 = AppUserFactory.create(user=UserFactory(username='tester2'))
        existing_user3 = AppUserFactory.create(user=UserFactory(username='tester3'))
        self.existing_users = [existing_user1, existing_user2, existing_user3]
        self.valid_url = reverse('friend') + '?username=' + self.search_term
        return super().setUp() 
    
    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_SearchFriendViewReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url)
        self.assertEqual(response.status_code, 200)
    
    def test_SearchFriendViewReturnCorrectContextData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.valid_url)
        self.assertEqual(response.context['users'], self.existing_users)

class RemoveFriendEndPointTest(APITestCase):
    app_user = None
    other_app_user = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory.create(friends=[self.other_app_user])
        self.other_app_user.friends.add(self.app_user)
        self.call_url = reverse('remove-friend')
        return super().setUp()

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_RemoveFriendTestRemoveSuccessfully(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"username": self.other_app_user.user.username}),  content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_RemoveFriendReturnErrorCode(self):
        self.client.force_login(user=self.app_user.user)
        invalid_username = 'XXXXX'
        response = self.client.post(path=self.call_url, data=json.dumps({"username": invalid_username}),  content_type="application/json")
        self.assertEqual(response.status_code, 404)
        response = self.client.post(path=self.call_url, data=json.dumps({}),  content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_FriendIsSuccessfullyRemoved(self):
        friend_count_of_remover = len(self.app_user.friends.all())
        removed_user_friend_count = len(self.other_app_user.friends.all())
        self.client.force_login(user=self.app_user.user)
        self.client.post(path=self.call_url, data=json.dumps({"username": self.other_app_user.user.username}),  content_type="application/json")
        self.assertEqual(len(self.app_user.friends.all()),friend_count_of_remover - 1)
        self.assertEqual(len(self.other_app_user.friends.all()),removed_user_friend_count - 1)

class DeclineFriendRequestEndPointTest(APITestCase):
    app_user = None
    other_app_user = None
    friend_request = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory()
        self.friend_request = FriendRequestFactory(sender=self.other_app_user, receiver=self.app_user)
        self.call_url = reverse('decline_friend_request')
        return super().setUp()

    def tearDown(self):
        FriendRequest.objects.all().delete()
        FriendRequestFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_FriendRequestDeclineSuccessCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}),  content_type="application/json")
        self.assertEquals(response.status_code, 200)

    def test_FriendRequestDeclineSuccessfully(self):
        self.client.force_login(user=self.app_user.user)
        self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}),  content_type="application/json")
        friend_request = FriendRequest.objects.get(id=self.friend_request.id)
        self.assertFalse(friend_request.pending)
    
    def test_FriendRequestDeclineFailureCode(self):
        self.client.force_login(user=self.other_app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}),  content_type="application/json")
        self.assertEquals(response.status_code, 400)
        invalid_request_id = '123'
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id": invalid_request_id}),  content_type="application/json")
        self.assertEquals(response.status_code, 404)
        invalid_request_id = 'XXX'
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id": invalid_request_id}),  content_type="application/json")
        self.assertEquals(response.status_code, 404)
        response = self.client.post(path=self.call_url, data=json.dumps({}),  content_type="application/json")
        self.assertEquals(response.status_code, 404)

class AcceptFriendRequestEndPointTest(APITestCase):
    app_user = None
    other_app_user = None
    friend_request = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory()
        self.friend_request = FriendRequestFactory(sender=self.other_app_user, receiver=self.app_user)
        self.call_url = reverse('accept_friend_request')
        return super().setUp()

    def tearDown(self):
        FriendRequest.objects.all().delete()
        FriendRequestFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_FriendRequestAcceptSuccessCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}),  content_type="application/json")
        self.assertEquals(response.status_code, 200)

    def test_FriendRequestAcceptSuccessfully(self):
        self.client.force_login(user=self.app_user.user)
        self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}),  content_type="application/json")
        friend_request = FriendRequest.objects.get(id=self.friend_request.id)
        self.assertFalse(friend_request.pending)

    def test_FriendListUpdatedForBothUsers(self):
        self.client.force_login(user=self.app_user.user)
        self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}),  content_type="application/json")
        self.assertIn(self.other_app_user, list(self.app_user.friends.all()))
        self.assertIn(self.app_user, list(self.other_app_user.friends.all()))

    def test_FriendRequestNotAuthorized(self):
        not_correct_app_user = AppUserFactory()
        self.client.force_login(user=not_correct_app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id": self.friend_request.id}), content_type="application/json")
        self.assertEqual(response.status_code, 405)

    def test_AcceptBadRequestErrorCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"request_id":123}), content_type="application/json")
        self.assertEquals(response.status_code, 404)
        response = self.client.post(path=self.call_url, data=json.dumps({"":""}), content_type="application/json")
        self.assertEquals(response.status_code, 400)

class CreateFriendRequestEndPointTest(APITestCase):
    app_user = None
    other_app_user = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory()
        self.call_url = reverse('send_friend_request')
        return super().setUp()  

    def tearDown(self):
        FriendRequest.objects.all().delete()
        FriendRequestFactory.reset_sequence()
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_CreateRequestSuccessCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"receiver": self.other_app_user.user.username}),  content_type="application/json")
        self.assertEquals(response.status_code, 200)

    def test_FriendRequestCreatedSuccessfully(self):
        self.client.force_login(user=self.app_user.user)
        self.client.post(path=self.call_url, data=json.dumps({"receiver": self.other_app_user.user.username}),  content_type="application/json")
        self.assertTrue(FriendRequest.objects.filter(sender=self.app_user, receiver=self.other_app_user).exists())

    def test_FriendRequestAcceptedSuccessfullyWhenPendingRequestExists(self):
        pending_friend_request = FriendRequestFactory(sender=self.other_app_user, receiver=self.app_user)
        self.client.force_login(user=self.app_user.user)
        self.client.post(path=self.call_url, data=json.dumps({"receiver": self.other_app_user.user.username}),  content_type="application/json")
        self.assertIn(self.other_app_user, list(self.app_user.friends.all()))
        self.assertIn(self.app_user, list(self.other_app_user.friends.all()))
        pending_friend_request = FriendRequest.objects.get(id=pending_friend_request.id)
        self.assertFalse(pending_friend_request.pending)

    def test_CreateBadRequestErrorCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(path=self.call_url, data=json.dumps({"bad":"value"}),  content_type="application/json")
        self.assertEquals(response.status_code, 400)

class ProfileFriendsViewTest(APITestCase):
    app_user = None
    other_app_user = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory()
        self.call_url = reverse('profile-friends')
        return super().setUp()  

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_ProfileFriendsViewReturnSuccessCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        self.assertEquals(response.status_code, 200)
        url_with_own_username = self.call_url + '?username=' + self.app_user.user.username
        response = self.client.get(url_with_own_username)
        self.assertEquals(response.status_code, 200)
        url_with_other_username = self.call_url + '?username=' + self.other_app_user.user.username
        response = self.client.get(url_with_other_username)
        self.assertEquals(response.status_code, 200)

    def test_ProfileFriendsViewReturnErrorCode(self):
        self.client.force_login(user=self.app_user.user)
        invalid_username = 'XXX'
        url_with_invalid_username = self.call_url + '?username=' + invalid_username
        response = self.client.get(url_with_invalid_username)
        self.assertEquals(response.status_code, 404)

    def test_ProfileFriendsViewReturnCorrectContext(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        app_user_context = response.context.get('app_user')
        self.assertEqual(app_user_context, self.app_user)

        url_with_other_username = self.call_url + '?username=' + self.other_app_user.user.username
        response = self.client.get(url_with_other_username)
        app_user_context = response.context.get('app_user')
        self.assertEqual(app_user_context, self.other_app_user)

        url_with_own_username = self.call_url + '?username=' + self.app_user.user.username
        response = self.client.get(url_with_own_username)
        app_user_context = response.context.get('app_user')
        self.assertEqual(app_user_context, self.app_user)
    
    def test_ProfileFriendsViewReturnCorrectTemplate(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        templates = response.templates
        template_names = [template.name for template in templates]
        self.assertIn('profile_friends.html', template_names)

        url_with_other_username = self.call_url + '?username=' + self.other_app_user.user.username
        response = self.client.get(url_with_other_username)
        templates = response.templates
        template_names = [template.name for template in templates]
        self.assertIn('user_friends.html', template_names)

        url_with_own_username = self.call_url + '?username=' + self.app_user.user.username
        response = self.client.get(url_with_own_username)
        templates = response.templates
        template_names = [template.name for template in templates]
        self.assertIn('profile_friends.html', template_names)

class SettingsViewTest(APITestCase):
    app_user = None
    other_app_user = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory()
        self.call_url = reverse('settings')
        return super().setUp()  

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()
    
    def test_SettingsViewReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        self.assertEqual(response.status_code, 200)

    def test_SettingsViewReturnCorrectContext(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        change_profile_picture_form = response.context['change_profile_picture_form']
        self.assertEqual(type(change_profile_picture_form), ChangeProfilePictureForm)
        password_change_form = response.context['password_change_form']
        self.assertEqual(type(password_change_form), PasswordChangeForm)

class ProfileViewTest(APITestCase):
    app_user = None
    app_user_posts = []
    other_app_user = None
    call_url = ''

    def setUp(self):
        self.other_app_user = AppUserFactory()
        self.app_user = AppUserFactory()
        self.app_user_posts = PostFactory.create_batch(size=3, user=self.app_user)
        self.other_app_user_posts = PostFactory.create_batch(size=3, user=self.other_app_user)
        self.call_url = reverse('profile')
        return super().setUp()  

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        FriendRequest.objects.all().delete()
        FriendRequestFactory.reset_sequence()
        return super().tearDown()

    def test_ProfileViewReturnSuccessStatusCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        self.assertEqual(response.status_code, 200)

    def test_ProfileViewReturnCorrectContextWithoutArgs(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url)
        isOwnProfile = response.context.get('isOwnProfile')
        self.assertTrue(isOwnProfile)
        posts = response.context.get('posts')
        self.assertCountEqual(self.app_user_posts, list(posts))
        app_user = response.context.get('app_user')
        self.assertEqual(self.app_user, app_user)

    def test_ProfileViewReturnCorrectContextWithOwnUsernameArgs(self):
        self.client.force_login(user=self.app_user.user)
        call_url_with_args = self.call_url + '?' + self.app_user.user.username
        response = self.client.get(call_url_with_args)
        isOwnProfile = response.context.get('isOwnProfile')
        self.assertTrue(isOwnProfile)
        posts = response.context.get('posts')
        self.assertCountEqual(self.app_user_posts, list(posts))
        app_user = response.context.get('app_user')
        self.assertEqual(self.app_user, app_user)

    def test_ProfileViewReturnCorrectContextWithOtherUsernameArgs(self):
        self.client.force_login(user=self.app_user.user)
        call_url_with_args = self.call_url + '?username=' + self.other_app_user.user.username
        response = self.client.get(call_url_with_args)
        isOwnProfile = response.context.get('isOwnProfile')
        self.assertFalse(isOwnProfile)
        posts = response.context.get('posts')
        self.assertCountEqual(self.other_app_user_posts, list(posts))
        app_user = response.context.get('app_user')
        self.assertEqual(self.other_app_user, app_user)

    def test_ProfileViewReturnCorrecFriendshipStatusContext(self):
        self.client.force_login(user=self.app_user.user)
        call_url_with_args = self.call_url + '?username=' + self.other_app_user.user.username
        response = self.client.get(call_url_with_args)
        app_user = response.context.get('app_user')
        self.assertEqual(app_user.friendship_status, 0)

        FriendRequestFactory.create(sender=self.app_user, receiver=self.other_app_user)
        response = self.client.get(call_url_with_args)
        app_user = response.context.get('app_user')
        self.assertEqual(app_user.friendship_status, 1)

        self.app_user.friends.add(self.other_app_user)
        self.other_app_user.friends.add(self.app_user)
        response = self.client.get(call_url_with_args)
        app_user = response.context.get('app_user')
        self.assertEqual(app_user.friendship_status, 2)

class ChangeProfileEndPointTest(APITestCase):
    app_user = None
    call_url = None

    def setUp(self):
        self.app_user = AppUserFactory()
        self.call_url = reverse('change_profile_picture')
        return super().setUp()  

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        return super().tearDown()

    def test_ChangeProfileEndPointSuccessCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(self.call_url, {})
        self.assertEqual(response.status_code, 200)

    def test_ChangeProfileEndPointWithInvalidData(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.post(self.call_url, {})
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status'], 'failure')

    # def test_ChangeProfileEndPointWithValidData(self):
    #     self.client.force_login(user=self.app_user.user)
    #     upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/profile-pic.png'), 'rb')
    #     file_dict = {'profile_image': SimpleUploadedFile(upload_file.name, content=upload_file.read(), content_type='image/jpeg')}
    #     response = self.client.post(self.call_url, file_dict)
    #     response_data = json.loads(response.content)
    #     self.assertTrue(response_data['status'])
    #     self.assertEqual(response_data['status'], 'success')

    def test_ChangeProfileEndPointWithWrongFileFormat(self):
        self.client.force_login(user=self.app_user.user)
        upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/default-profile-pic.svg'), 'rb')
        file_dict = {'profile_image': SimpleUploadedFile(upload_file.name, content=upload_file.read(), content_type='image/jpeg')}
        response = self.client.post(self.call_url, file_dict)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status'], 'failure')

class UserPostEndPointTest(APITestCase):
    app_user = None
    call_url = None
    user_post = None

    def setUp(self):
        self.app_user = AppUserFactory()
        self.user_post = PostFactory(user=self.app_user)
        self.call_url = reverse('user_post')
        self.invalid_post_id = '999'
        return super().setUp()  

    def tearDown(self):
        AppUser.objects.all().delete()
        AppUserFactory.reset_sequence()
        User.objects.all().delete()
        UserFactory.reset_sequence()
        Post.objects.all().delete()
        PostFactory.reset_sequence()
        return super().tearDown()

    def test_GetUserPostEndPointTestSuccessCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url + '?id=' + str(self.user_post.id))
        self.assertEqual(response.status_code, 200)

    def test_GetUserPostEndPointTestErrorCode(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url + '?id=' + self.invalid_post_id)
        self.assertEqual(response.status_code, 404)

    def test_GetUserPostEndPointReturnCorrectPost(self):
        self.client.force_login(user=self.app_user.user)
        response = self.client.get(self.call_url + '?id=' + str(self.user_post.id))
        post = response.context.get('post')
        self.assertEqual(post.text, self.user_post.text)
        self.assertEqual(post.id, self.user_post.id)

    def test_CreateUserPostEndPointWithValidData(self):
        self.client.force_login(user=self.app_user.user)
        upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/profile-pic.png'), 'rb')
        valid_dict = {
            'text': 'text', 
            'image': SimpleUploadedFile(upload_file.name, content=upload_file.read(), content_type='image/jpeg'
        )}
        response = self.client.post(self.call_url, valid_dict)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status'], 'success')

        valid_dict = {'text': 'text'}
        response = self.client.post(self.call_url, valid_dict)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status'], 'success')

    def test_CreateUserPostEndPointWithInvalidData(self):
        self.client.force_login(user=self.app_user.user)
        upload_file = open(os.path.join(settings.MEDIA_ROOT, 'default/default-profile-pic.svg'), 'rb')
        invalid_dict = {
            'text': 'text', 
            'image': SimpleUploadedFile(upload_file.name, content=upload_file.read()
        )}
        response = self.client.post(self.call_url, invalid_dict)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status'], 'failure')

        invalid_dict = {
            'image': SimpleUploadedFile(upload_file.name, content=upload_file.read()
        )}
        response = self.client.post(self.call_url, invalid_dict)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data['status'], 'failure')


class ChatEndPointTest(APITestCase):
    sending_user = None
    receiving_user = None
    messages = []
    chat_room = None

    def setUp(self):
        self.sending_user = AppUserFactory()
        self.receiving_user = AppUserFactory()
        self.chat_room = ChatRoomFactory.create(participants=[self.sending_user, self.receiving_user])
        self.messages = MessageFactory.create_batch(size=3, chat_room=self.chat_room)
       
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

    def test_ChatEndPointReturnSuccessCode(self):
        self.client.force_login(user=self.sending_user.user)
        call_url = reverse('chat', kwargs={'target_username':self.receiving_user.user.username})
        response = self.client.get(call_url)
        self.assertEqual(response.status_code, 200)

    def test_ChatEndPointReturnCorrectTargetUser(self):
        self.client.force_login(user=self.sending_user.user)
        call_url = reverse('chat', kwargs={'target_username':self.receiving_user.user.username})
        response = self.client.get(call_url)
        target_user = response.context.get('target_user')
        self.assertEqual(target_user, self.receiving_user)

    def test_ChatEndPointReturnCorrectChatRoom(self):
        self.client.force_login(user=self.sending_user.user)
        call_url = reverse('chat', kwargs={'target_username':self.receiving_user.user.username})
        response = self.client.get(call_url)
        chat_room_id = response.context.get('chat_room_id')
        self.assertEqual(chat_room_id, self.chat_room.id)

    def test_ChatEndPointReturnMessages(self):
        self.client.force_login(user=self.sending_user.user)
        call_url = reverse('chat', kwargs={'target_username':self.receiving_user.user.username})
        response = self.client.get(call_url)
        messages = response.context.get('messages')
        self.assertEqual(len(messages), len(self.messages))
        self.assertListEqual(self.messages, messages)

    def test_ChatEndPointReturnMessageData(self):
        self.client.force_login(user=self.sending_user.user)
        call_url = reverse('chat', kwargs={'target_username':self.receiving_user.user.username})
        response = self.client.get(call_url)
        messages = response.context.get('messages')
        for i in range(len(messages)):
            self.assertEqual(self.messages[i].id, messages[i].id)
            self.assertEqual(self.messages[i].chat_room, messages[i].chat_room)
            self.assertEqual(self.messages[i].text, messages[i].text)
            self.assertEqual(self.messages[i].sender, messages[i].sender)
            self.assertEqual(self.messages[i].timestamp, messages[i].timestamp)