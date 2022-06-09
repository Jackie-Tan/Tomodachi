from django.shortcuts import redirect
from . import views
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views  import *
from . import apis
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login_required()(views.index), name='index'),
    path('explore/', login_required()(views.explore), name='explore'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('password-change-success/', views.password_change_success, name='password_change_success'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', login_required()(views.user_logout), name='logout'),
    path('friend/', login_required()(views.search_friend), name='friend'),
    path('profile/', login_required()(views.profile), name='profile'),
    path('profile-friends/', login_required()(views.profile_friends), name='profile-friends'),
    path('friend-list/', login_required()(views.friend_list), name='friend-list'),
    path('post/', login_required()(views.user_post), name='user_post'),
    path('settings/', login_required()(views.settings), name='settings'),
    path('requests/', login_required()(views.friend_requests), name='requests'),
    path('send-friend-request/', login_required()(views.send_friend_request), name='send_friend_request'),
    path('accept-friend-request/', login_required()(views.accept_friend_request), name='accept_friend_request'),
    path('decline-friend-request/', login_required()(views.decline_friend_request), name='decline_friend_request'),
    path('remove-friend/', login_required()(views.remove_friend), name='remove-friend'),
    path('chat/<str:target_username>/', login_required()(views.chats), name='chat'),
    path('change-profile-picture/', login_required()(views.change_profile_picture), name='change_profile_picture'),
    path('api/explore', apis.RetrieveAllPosts.as_view(), name='explore_api'),
    path('api/post/<str:id>', apis.RetrievePost.as_view(), name='post_api'),
    path('api/posts/<str:username>', apis.RetrieveUserPosts.as_view(), name='user_posts_api'),
    path('api/friends/<str:username>', apis.RetrieveAppUserFriends.as_view(), name='user_friends_api'),
    path('api/user/<str:username>', apis.RetrieveAppUserDetails.as_view(), name='user_api'),
    path('api/feed', apis.RetrieveFeedPosts.as_view(), name='feed_api'),
    path('api/pending-friend-requests/', apis.RetrievePendingFriendRequests.as_view(), name='pending_friend_requests_api'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)