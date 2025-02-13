import requests
from django.conf import settings
from django.http import JsonResponse

def get_or_create_mattermost_user(user):
    headers = {"Authorization": f"Bearer {settings.MATTERMOST_ADMIN_TOKEN}"}

    # 1. Check if the user exists
    response = requests.get(f"{settings.MATTERMOST_API_URL}/users/email/{user.email}", headers=headers)

    if response.status_code == 200:
        # User exists, return their ID
        return response.json().get("id")
    
    elif response.status_code == 404:
        # 2. User does not exist, create them
        data = {
            "email": user.email,
            "username": user.username,
            "password": "some-random-password",  # Change if needed
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        response = requests.post(f"{settings.MATTERMOST_API_URL}/users", json=data, headers=headers)

        if response.status_code == 201:
            return response.json().get("id")

    return None

def login_to_mattermost(request):
    """Automatically logs in the user to Mattermost and returns their session token."""
    user = request.user  # Assuming user is authenticated in Django
    if not user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    mm_user_id = get_or_create_mattermost_user(user)
    if not mm_user_id:
        return JsonResponse({"error": "Failed to log in user to Mattermost"}, status=500)

    # 3. Get a session token for the user
    data = {"login_id": user.email, "password": "some-random-password"}
    response = requests.post(f"{settings.MATTERMOST_API_URL}/users/login", json=data)

    if response.status_code == 200:
        token = response.headers.get("Token")
        return JsonResponse({"message": "Logged into Mattermost successfully!", "token": token})
    
    return JsonResponse({"error": "Mattermost login failed", "details": response.json()}, status=400)
