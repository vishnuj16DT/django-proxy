from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

class MattermostProxyView(APIView):
    def get_mattermost_headers(self, request):
        """Extract Mattermost auth cookie and create headers"""
        headers = {
            'Content-Type': 'application/json',
        }
        print("Request : ", request)
        print("Request Headers : ", request.headers)
        print("Request Cookies : ", request.COOKIES)
        
        mm_token = request.COOKIES.get('MMAUTHTOKEN')
        mm_csrf = request.COOKIES.get('csrftoken')
        if mm_token:
            headers['Cookie'] = f'MMAUTHTOKEN={mm_token}\nMMCSRF={mm_csrf}'
        
        if request.method == "POST":
            headers['X-CSRF-TOKEN'] = mm_csrf
        
        return headers

    def proxy_request(self, request, path, method='GET', data=None):
        """Generic method to proxy requests to Mattermost"""
        url = f"{settings.MATTERMOST_API_URL}/{path}"
        headers = self.get_mattermost_headers(request)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                cookies=request.COOKIES
            )
            
            print("Response : ", response.json())
            print("Response Cookies : ", response.cookies)
            print("Response Headers : ", response.headers)
            print("Token : ", response.headers['Token'])
            data = response.json()

            django_response = Response(
                data=response.json() if response.content else None,
                status=response.status_code
            )
            
            if 'set-cookie' in response.headers:
                django_response['Set-Cookie'] = response.headers['set-cookie']
                
            return django_response
            
        except requests.RequestException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(MattermostProxyView):
    def post(self, request):
        return self.proxy_request(
            request,
            'users/login',
            method='POST',
            data=request.data
        )

class LogoutView(MattermostProxyView):
    def post(self, request):
        return self.proxy_request(
            request,
            'users/logout',
            method='POST'
        )

class CurrentUserView(MattermostProxyView):
    def get(self, request):
        return self.proxy_request(request, 'users/me')

class TeamsView(MattermostProxyView):
    def get(self, request):
        return self.proxy_request(request, 'users/me/teams')

class TeamMembersView(MattermostProxyView):
    def get(self, request, team_id):
        return self.proxy_request(
            request,
            f'teams/{team_id}/members'
        )

class ChannelsView(MattermostProxyView):
    def get(self, request, team_id):
        return self.proxy_request(
            request,
            f'users/me/teams/{team_id}/channels'
        )
    
    def post(self, request):
        return self.proxy_request(
            request,
            'channels',
            method='POST',
            data=request.data
        )

class ChannelMembersView(MattermostProxyView):
    def post(self, request, channel_id):
        return self.proxy_request(
            request,
            f'channels/{channel_id}/members',
            method='POST',
            data=request.data
        )

class DirectChannelView(MattermostProxyView):
    def post(self, request):
        return self.proxy_request(
            request,
            'channels/direct',
            method='POST',
            data=request.data
        )

class UserDetailsView(MattermostProxyView):
    def get(self, request, user_id):
        return self.proxy_request(
            request,
            f'users/{user_id}'
        )

class PostsView(MattermostProxyView):
    def get(self, request, channel_id):
        include_deleted = request.query_params.get('include_deleted', False)
        return self.proxy_request(
            request,
            f'channels/{channel_id}/posts?include_deleted={include_deleted}'
        )
    
    def post(self, request):
        return self.proxy_request(
            request,
            'posts',
            method='POST',
            data=request.data
        )
    
    def delete(self, request, post_id):
        return self.proxy_request(
            request,
            f'posts/{post_id}',
            method='DELETE'
        )

class ReactionsView(MattermostProxyView):
    def post(self, request):
        return self.proxy_request(
            request,
            'reactions',
            method='POST',
            data=request.data
        )

    def delete(self, request, post_id, emoji_name):
        return self.proxy_request(
            request,
            f'users/me/posts/{post_id}/reactions/{emoji_name}',
            method='DELETE'
        )
