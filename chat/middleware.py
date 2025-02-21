import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from accounts.models import MMUser
from django.db import close_old_connections
import asyncio

class JWTAuthMiddleware(BaseMiddleware):
    """Custom middleware for JWT authentication in Django Channels"""
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        print("Middleware is running")
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]  # Extract token from query params
        print("Token from QP : ", token)

        scope["user"] = AnonymousUser()  # Default to anonymous

        if token:
            try:
                # Decode JWT Token
                decoded_data = jwt.decode(token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=["HS256"])
                print("Decoded data : ", decoded_data)
                user_id = decoded_data.get("user_id")

                # Get the Mattermost user
                user = await self.get_mm_user(user_id)
                print("Got the User : ", user)
                if user:
                    scope["user"] = user  # Attach user to scope

            except jwt.ExpiredSignatureError:
                print("JWT Token expired")
            except jwt.InvalidTokenError:
                print("Invalid JWT Token")

        close_old_connections()
        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_mm_user(user_id):
        """Get the Mattermost user from DB asynchronously"""
        # from django.contrib.auth import get_user_model
        # User = get_user_model()
        
        try:
            return await asyncio.to_thread(MMUser.objects.get, id=user_id)
        except MMUser.DoesNotExist:
            return None

# Wrapper for easy usage in routing
def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
