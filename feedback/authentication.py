import os

from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


class CustomAuthentication(BaseAuthentication):
    @staticmethod
    def decode_jwt_token(request):
        auth_header = get_authorization_header(request).split()
        if not auth_header or auth_header[0].lower() != b'bearer':
            raise AuthenticationFailed('Invalid Authorization header')

        token = auth_header[1]

        try:
            auth_secret_key = os.getenv("AUTH_SECRET_KEY")
            decoded_token = jwt.decode(token, auth_secret_key, algorithms=['HS256'])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

    def authenticate(self, request):
        # Your custom authentication logic here
        # For example, check headers, tokens, or other credentials
        # If authentication fails, raise exceptions.AuthenticationFailed
        # If authentication succeeds, return (user, auth) tuple

        # Example: Authenticate based on a custom header
        custom_token = request.META.get('HTTP_X_PROFILE_TOKEN')
        if not custom_token:
            raise exceptions.AuthenticationFailed('Custom token missing')

        try:
            # user = User.objects.using("users").get(username=custom_token)
            # api_url = "https://localhost:4000/user"
            # headers = {'Authorization': 'Token'+custom_token}
            # requests.get()
            user = self.decode_jwt_token(request)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except Exception as err:
            raise err

        return (user, None)  # No additional authentication info

# In your views or viewsets, use this custom authentication class:
# class MyView(APIView):
#     authentication_classes = [ExampleAuthentication]
#     ...
