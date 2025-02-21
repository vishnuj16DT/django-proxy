from django.urls import path
from .views import (
    TeamView, ChannelView, UserTeamView, UserChannelView,
    MessageView, ReplyView, ReactionView
)

urlpatterns = [
    path('teams/', TeamView.as_view(), name='team-list-create'),
    path('teams/<str:team_id>/channels/', ChannelView.as_view(), name='team-channels'),
    path('teams/<str:team_id>/add-user/', UserTeamView.as_view(), name='add-user-to-team'),
    path('channels/', UserChannelView.as_view(), name='user-channels'),
    path('channels/<str:channel_id>/add-user/', UserChannelView.as_view(), name='add-user-to-channel'),
    path('channels/<str:channel_id>/messages/', MessageView.as_view(), name='send-message'),
    path('channels/<str:channel_id>/messages/', MessageView.as_view(), name='get-messages'),
    path('messages/<str:post_id>/delete/', MessageView.as_view(), name='delete-message'),
    path('messages/<str:post_id>/reply/', ReplyView.as_view(), name='reply-to-message'),
    path('messages/<str:post_id>/react/', ReactionView.as_view(), name='react-to-message'),
    path('messages/<str:post_id>/react/<str:emoji_name>/delete/', ReactionView.as_view(), name='delete-reaction'),
]
