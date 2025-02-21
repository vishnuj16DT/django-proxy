from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
import requests
from .models import MMUser

# Get the custom user model
# User = get_user_model()

def create_mattermost_user(email, username):
    """Create a Mattermost user via API and generate a personal access token."""
    payload = {
        "email": email,
        "username": username,
        "password": "SomeSecurePassword123!",
    }
    
    headers = {"Authorization": f"Bearer {settings.MATTERMOST_ADMIN_TOKEN}"}

    print("We are here")
    
    response = requests.post(f"{settings.MATTERMOST_API_URL}/users", json=payload, headers=headers)
    print("MM User creation response : ", response.json())

    if response.status_code in  [200, 201]:
        mattermost_user_id = response.json().get("id")
        print("User ID: ", response.json().get("id"))

        print("Get in")

        # Generate a personal access token
        token_payload = {
            "user_id": mattermost_user_id,
            "description": "User token for API access"
        }
        token_response = requests.post(f"{settings.MATTERMOST_API_URL}/users/{mattermost_user_id}/tokens",
                                       json=token_payload, headers=headers)
        print("Token for user creation response : ", token_response.json())
        print("Acytual Token : ", token_response.json().get("token"))
        
        if token_response.status_code in  [200, 201]:
            access_token = token_response.json().get("token")
            print("User ID : ", mattermost_user_id, "\nToken : ", access_token)
            return mattermost_user_id, access_token

    return None, None


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'Please provide username, email, and password'}, 
                        status=status.HTTP_400_BAD_REQUEST)

    if MMUser.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, 
                        status=status.HTTP_400_BAD_REQUEST)

    if MMUser.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, 
                        status=status.HTTP_400_BAD_REQUEST)

    mattermost_user_id, access_token = create_mattermost_user(email, username)
    user = MMUser.objects.create_user(username=username, email=email, password=password, mattermost_user_id=mattermost_user_id, mattermost_access_token=access_token)

    # Create Mattermost user
    # mattermost_user_id, access_token = create_mattermost_user(user)

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'User created successfully',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'email': user.email,
        'mattermost_user_id': mattermost_user_id,
        'mattermost_access_token': access_token
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Please provide both username and password'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # If Mattermost details are missing, create them
    if not user.mattermost_user_id:
        # if user.username=='vishnu':
        #     user.mattermost_access_token = settings.MATTERMOST_ADMIN_TOKEN
        #     user.mattermost_user_id = "3438qg3ixt86mr7qjrm37t5a9r"
        #     user.save()

        mattermost_user_id, access_token = create_mattermost_user(user.email, user.username)
    else:
        mattermost_user_id = user.mattermost_user_id
        access_token = user.mattermost_access_token

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'User logged in successfully',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username,
        'email': user.email,
        'mattermost_user_id': mattermost_user_id,
        'mattermost_access_token': access_token
    }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
