from django.urls import path
from .views import (
    LoginView, LogoutView, CurrentUserView, TeamsView, 
    TeamMembersView, ChannelsView, ChannelMembersView,
    DirectChannelView, UserDetailsView, PostsView,
    ReactionsView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/<str:user_id>/', UserDetailsView.as_view(), name='user-details'),
    path('teams/', TeamsView.as_view(), name='teams'),
    path('teams/<str:team_id>/members/', TeamMembersView.as_view(), name='team-members'),
    path('teams/<str:team_id>/channels/', ChannelsView.as_view(), name='team-channels'),
    path('channels/', ChannelsView.as_view(), name='channels'),
    path('channels/direct/', DirectChannelView.as_view(), name='direct-channel'),
    path('channels/<str:channel_id>/members/', ChannelMembersView.as_view(), name='channel-members'),
    path('channels/<str:channel_id>/posts/', PostsView.as_view(), name='channel-posts'),
    path('posts/', PostsView.as_view(), name='posts'),
    path('posts/<str:post_id>/', PostsView.as_view(), name='delete-post'),
    path('reactions/', ReactionsView.as_view(), name='reactions'),
    path('users/me/posts/<str:post_id>/reactions/<str:emoji_name>/', ReactionsView.as_view(), name='remove-reaction'),
]