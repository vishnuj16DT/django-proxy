from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import requests
from accounts.models import MMUser

class TeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new team in Mattermost"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}

        team_type = request.data.get("type")  # Get the team type from the request

        if team_type is None:  # Check if it's not provided
            team_type = "O"  # Set default to "O"
        elif not team_type: # Check if it's empty string ""
            team_type = "O"

        payload = {
            "name": request.data.get("name"),
            "display_name": request.data.get("display_name"),
            "type": team_type
        }
        response = requests.post(f"{settings.MATTERMOST_API_URL}/teams", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)

    def get(self, request):
        """List all teams"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.get(f"{settings.MATTERMOST_API_URL}/teams", headers=headers)
        return Response(response.json(), status=response.status_code)
    
    def delete(self, request, team_id, user_id):
        """Remove a user from a team"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.delete(f"{settings.MATTERMOST_API_URL}/teams/{team_id}/members/{user_id}", headers=headers)
        return Response(response.json(), status=response.status_code)

class ChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        """Create a new channel in a team"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        team_type = request.data.get("type")  # Get the team type from the request

        if team_type is None:  # Check if it's not provided
            team_type = "O"  # Set default to "O"
        elif not team_type: # Check if it's empty string ""
            team_type = "O"

        payload = {
            "team_id": team_id,
            "name": request.data.get("name"),
            "display_name": request.data.get("display_name"),
            "type": team_type
        }
        response = requests.post(f"{settings.MATTERMOST_API_URL}/channels", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)

    def get(self, request, team_id):
        """List all channels within a team"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.get(f"{settings.MATTERMOST_API_URL}/teams/{team_id}/channels", headers=headers)
        return Response(response.json(), status=response.status_code)

    def delete(self, request, channel_id, user_id):
        """Remove a user from a channel"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.delete(f"{settings.MATTERMOST_API_URL}/channels/{channel_id}/members/{user_id}", headers=headers)
        return Response(response.json(), status=response.status_code)
class UserTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        user_id = request.data.get("user_id")
        if not user_id:
            user_id = user.mattermost_user_id
        
        payload = {"team_id": team_id, "user_id": user_id}
        response = requests.post(f"{settings.MATTERMOST_API_URL}/teams/{team_id}/members", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)

class UserChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        """Add user to a channel"""
        user = request.user
        user_id = request.data.get("user_id")
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        if not user_id:
            user_id = user.mattermost_user_id
        payload = {"user_id": user_id}
        response = requests.post(f"{settings.MATTERMOST_API_URL}/channels/{channel_id}/members", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)

    def get(self, request):
        """List all channels the user is part of"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.get(f"{settings.MATTERMOST_API_URL}/users/{user.mattermost_user_id}/channels", headers=headers)
        return Response(response.json(), status=response.status_code)

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        """Send a message to a channel"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        payload = {
            "channel_id": channel_id,
            "message": request.data.get("message")
        }
        response = requests.post(f"{settings.MATTERMOST_API_URL}/posts", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)

    def delete(self, request, post_id):
        """Delete a message"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.delete(f"{settings.MATTERMOST_API_URL}/posts/{post_id}", headers=headers)
        return Response(response.json(), status=response.status_code)
    
    def get(self, request, channel_id):
        """Retrieve all messages from a channel"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.get(f"{settings.MATTERMOST_API_URL}/channels/{channel_id}/posts", headers=headers)
        return Response(response.json(), status=response.status_code)

class ReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """Reply to a message"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        payload = {
            "channel_id": request.data.get("channel_id"),
            "message": request.data.get("message"),
            "root_id": post_id
        }
        response = requests.post(f"{settings.MATTERMOST_API_URL}/posts", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)

class ReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """React to a message"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        payload = {
            "user_id": user.mattermost_user_id,
            "post_id": post_id,
            "emoji_name": request.data.get("emoji")
        }
        response = requests.post(f"{settings.MATTERMOST_API_URL}/reactions", json=payload, headers=headers)
        return Response(response.json(), status=response.status_code)
    
    def delete(self, request, post_id, emoji_name):
        """Remove a reaction from a message"""
        user = request.user
        headers = {"Authorization": f"Bearer {user.mattermost_access_token}"}
        response = requests.delete(f"{settings.MATTERMOST_API_URL}/users/{user.mattermost_user_id}/posts/{post_id}/reactions/{emoji_name}", headers=headers)
        return Response(response.json(), status=response.status_code)