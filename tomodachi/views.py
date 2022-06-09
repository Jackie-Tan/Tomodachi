import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .forms import *
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db import transaction
from .model_factories import *

@login_required
def index(request):
    '''
        Renders the main page of the web app which consist of a post creation form and display posts by users the user is following
    '''
    try:
        app_user = AppUser.objects.get(user=request.user)
        post_form = PostForm()
        return render(request, 'index.html', {"app_user" : app_user, "post_form" : post_form})
    except AppUser.DoesNotExist:
        return HttpResponse(status=404, content="User does not exists")

def sign_up(request):
    '''
        Renders the account creation page
    '''
    # Checks if the user is already authenticated and redirects the user to the root of the web app if already is
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        else:
             user_form = UserCreationForm()
             return render(request, 'sign-up.html', {'form' : user_form})
    # Checks if the user is signing up for a new account and redirects the to the root of the web if sign up is access         
    if request.method == 'POST':
        user_form = UserCreationForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request, user)
            newAppUser = AppUser(user=user)
            newAppUser.save()
            return HttpResponseRedirect('/')
        else:
            # Display the relevant error messages if sign up details are invalid
            return render(request, 'sign-up.html', {'form':user_form})

@login_required
def user_logout(request):
    '''
        Logs the user out and redirects the user to the root of the web app
    '''
    logout(request)
    return HttpResponseRedirect('/login/')


@login_required
def search_friend(request):
    '''
        Displays users with usernames like the request username
    '''
    if request.method == 'GET':
        requested_username = request.GET.get('username', '')
        if requested_username:
            matched_user_records = AppUser.objects.filter(user__username__contains=requested_username)
            matched_users = list(matched_user_records.all())
            current_user = AppUser.objects.get(user=request.user)
            for matched_user in matched_users:
                if matched_user.user.username == request.user.username:
                    matched_users.remove(matched_user)
                    break
            return render(request, 'search_user.html', {"requested_username" : requested_username, "users": matched_users, "current_user" : current_user})

@login_required 
def profile(request):
    '''
        Displays user posts and friend status with the existing user
    '''
    if request.method == 'GET':
            requested_username = request.GET.get('username') 
            if requested_username: # if user agent requests for other person profile
                if requested_username == request.user.username:
                    return HttpResponseRedirect('/profile/?' + requested_username)
                app_user = AppUser.objects.get(user__username=requested_username)
                posts = Post.objects.filter(user=app_user).order_by('-timestamp')
                requester = AppUser.objects.get(user=request.user)
                if app_user in requester.friends.all():
                    app_user.friendship_status = 2 # already friends
                else:
                    try:
                        FriendRequest.objects.get(sender=requester, receiver=app_user, pending=True)
                        app_user.friendship_status = 1 # not friends but request sent
                    except FriendRequest.DoesNotExist:
                        app_user.friendship_status = 0 # not friends and no request yet
                return render(request, 'profile.html', {"app_user" : app_user, "posts" : posts, "isOwnProfile": False})
            else: 
                app_user = AppUser.objects.get(user=request.user)
                posts = Post.objects.filter(user=app_user).order_by('-timestamp')
                return render(request, 'profile.html', {"app_user" : app_user, "posts" : posts, "isOwnProfile" : True})

@login_required
def profile_friends(request):
    '''
        Display the appropriate template for displaying the app user's friends or the current user's friends
    '''
    if request.method == 'GET':
        requested_username = request.GET.get('username', '')
        try:
            if requested_username:
                # Return own profile friends template
                if requested_username == request.user.username:
                    app_user = AppUser.objects.get(user=request.user)
                    return render(request, 'profile_friends.html', {'app_user' : app_user})
                # Return other user profile friends template
                else:
                    app_user = AppUser.objects.get(user__username=requested_username)
                    return render(request, 'user_friends.html', {'app_user' : app_user})
            else:
                # Return own profile friends template if not username is provided
                app_user = AppUser.objects.get(user=request.user)
                return render(request, 'profile_friends.html', {'app_user' : app_user})
        except AppUser.DoesNotExist:
            return HttpResponse(status=404, content="User does not exists")

@login_required
def friend_list(request):
    '''
        Returns a page where the user can view his/her list of friends
    '''
    return render(request, 'friend_list.html')

@login_required 
def change_profile_picture(request):
    '''
        Endpoint for user to change this display photo
    '''
    if request.method == 'POST':
        change_profile_picture_form = ChangeProfilePictureForm(data=request.POST, files=request.FILES)
        if change_profile_picture_form.is_valid():
            try:
                app_user = AppUser.objects.get(user=request.user) 
                app_user.profile_image = change_profile_picture_form.cleaned_data['profile_image']
                app_user.save()
                return JsonResponse({'status': 'success'})
            except AppUser.DoesNotExist:
                return JsonResponse({'status': 'failure', 'messages' : {'user': 'Does not exist'}})
        else:
            response_dict = {'status' : 'failure'}
            errors_dict = dict(change_profile_picture_form.errors.items())
            response_dict['messages'] = errors_dict
            return JsonResponse(response_dict)

@login_required 
def user_post(request):
    '''
        Endpoint for user to create post
    '''
    if request.method == 'POST':
        post_form = PostForm(data=request.POST, files=request.FILES)
        if post_form.is_valid():
            try:
                post = post_form.save(commit=False)
                post.user = AppUser.objects.get(user=request.user)
                post.save()
                return JsonResponse({'status': 'success'})
            except:
                return HttpResponse(status=404, content='User not found')
        else:
            response_dict = {'status' : 'failure'}
            errors_dict = dict(post_form.errors.items())
            response_dict['messages'] = errors_dict
            return JsonResponse(response_dict)

    if request.method == 'GET':
        try:
            requested_post_id = request.GET.get('id', '')
            post = Post.objects.get(id=requested_post_id)
            return render(request, 'post.html', {'post' : post})
        except Post.DoesNotExist:
            return HttpResponse(status=404, content='Post not found')

@login_required
def settings(request):
    '''
        Returns a page where the user can edit his/her account settings such as password and profile picture
    '''
    if request.method == 'GET':
        password_change_form = PasswordChangeForm(user=request.user)
        change_profile_picture_form = ChangeProfilePictureForm()
        return render(request, 'settings.html', {'change_profile_picture_form': change_profile_picture_form,'password_change_form' : password_change_form})
    if request.method == 'POST':
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        change_profile_picture_form = ChangeProfilePictureForm()
        if password_change_form.is_valid():
            password_change_form.save()
            return HttpResponseRedirect('/password-change-success/')
        else:
            return render(request, 'settings.html', {'change_profile_picture_form': change_profile_picture_form,'password_change_form' : password_change_form})

@login_required
def friend_requests(request):
    '''
        Returns the page where user can view pending friend requests
    '''
    if request.method == 'GET':
        return render(request, 'requests.html', {'username': request.user.username})

@login_required
@transaction.atomic
def send_friend_request(request):
    '''
        API endpoint for creating a friend request
    '''
    if request.method == 'POST':
        receiver = json.loads(request.body).get('receiver')
        if (receiver == None):
            return HttpResponse(status=400, content='No receiver included, bad request.')
        sender_record = AppUser.objects.get(user=request.user)
        receiver_record = AppUser.objects.get(user__username=receiver)
        try:
            with transaction.atomic():
            # receiver had already previously sent a friend request to the sender
            # hence make it auto accept request
                existingFriendRequest = FriendRequest.objects.get(sender=receiver_record, receiver=sender_record, pending=True)
                sender_record.friends.add(receiver_record)
                receiver_record.friends.add(sender_record)
                sender_record.save()
                receiver_record.save()
                existingFriendRequest.pending = False
                existingFriendRequest.save()
                return HttpResponse(status=200)
        except FriendRequest.DoesNotExist:
            new_friend_request = FriendRequest(sender=sender_record, receiver=receiver_record, pending=True)
            new_friend_request.save()
            return HttpResponse(status=200) # request successfully created
    return HttpResponse(status=404)

@login_required
def explore(request):
    '''
        Return the page where the user can view all posts posted
    '''
    if request.method == 'GET':
        return render(request, 'explore.html')


@login_required
@transaction.atomic
def accept_friend_request(request):
    '''
        API endpoint for accepting a friend
    '''
    if request.method == 'POST':
        data = json.loads(request.body)
        request_id = data.get('request_id')
        if request_id == None:
            return HttpResponse(status=400)
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
            if friend_request.receiver != AppUser.objects.get(user=request.user):
                return HttpResponse(status=405, content='THIS IS NOT FOR YOU TO ACCEPT')
            with transaction.atomic():
                sender = friend_request.sender
                receiver = friend_request.receiver
                friend_request.pending = False
                sender.friends.add(receiver)
                receiver.friends.add(sender)
                sender.save()
                receiver.save()
                friend_request.save()
                return HttpResponse(status=200)
        except FriendRequest.DoesNotExist:
            return HttpResponse(status=404)

@login_required
@transaction.atomic
def remove_friend(request):
    '''
        API endpoint for removing a friend
    '''
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'username' in data:
            username = data['username']
            try:
                remover = AppUser.objects.get(user=request.user)
                user_to_remove = AppUser.objects.get(user__username=username)
                with transaction.atomic():
                    remover.friends.remove(user_to_remove)
                    user_to_remove.friends.remove(remover)
                    remover.save()
                    user_to_remove.save()
                    return HttpResponse(status=200)
            except AppUser.DoesNotExist:
                return HttpResponse(status=404, content='Invalid username provided')
        else:
            return HttpResponse(status=404, content='No username provided')


@login_required
def decline_friend_request(request):
    '''
        API endpoint for declining a friend request
    '''
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'request_id' in data:
            request_id = data['request_id']
            if type(request_id) != int:
                return HttpResponse(status=404, content='Invalid request id provided')
            try: 
                friend_request = FriendRequest.objects.get(id=request_id)
                if AppUser.objects.get(user=request.user) == friend_request.receiver:
                    friend_request.pending = False
                    friend_request.save()
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=400, content='This is not your friend request to decline')
            except (AppUser.DoesNotExist, FriendRequest.DoesNotExist):
                return HttpResponse(status=404, content='Request user or request record does not exists')
        else:
            return HttpResponse(status=404, content='No request id provided')
            
@login_required
def chats(request, target_username):
    if request.method == 'GET':
        if request.user.username == target_username:
            return HttpResponse(status=400, content='You cannot message yourself')

        current_user = AppUser.objects.get(user=request.user)
        target_user = AppUser.objects.get(user__username=target_username)
        chat_room_id = ''
        messages = []
        existing_chat_queryset = ChatRoom.objects.filter(participants=current_user).filter(participants=target_user)
        if existing_chat_queryset:
            existing_chat_room = list(existing_chat_queryset)[0]
            chat_room_id = existing_chat_room.id
            messages = list(Message.objects.filter(chat_room=existing_chat_room))
        else:
            new_chat_room = ChatRoom()
            new_chat_room.save()
            new_chat_room.participants.add(current_user)
            new_chat_room.participants.add(target_user)
            new_chat_room.save()
            chat_room_id = new_chat_room.id

        return render(request, 'chat.html', {'target_user': target_user, 'chat_room_id': chat_room_id, 'messages' : messages})

def password_change_success(request):
    '''
        Returns the password redirect page upon password change success
    '''
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request, 'password_change_success.html')
