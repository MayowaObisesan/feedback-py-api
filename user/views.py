from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from feedback.models import FeedbackModel
from feedback.serializers import ListFeedbackSerializer
from user.models import User
from user.serializers import (
    ListUserSerializer, CustomTokenObtainPairSerializer, CreateUserSerializer, VerifyUserSerializer,
    ResendVerificationCodeSerializer, ForgotPasswordSerializer, VerifyForgotPasswordCodeSerializer,
    SetPasswordSerializer, ChangePasswordSerializer, GenerateStrongPasswordSerializer
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    authentication_classes = []
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['email', 'firstname', 'lastname', 'phone']
    ordering_fields = ['created_at', 'last_login', 'email', 'firstname', 'lastname', 'phone']

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return self.serializer_class

    @action(
        methods=["GET"], detail=False, permission_classes=[IsAuthenticated],
        authentication_classes=[JWTAuthentication], url_path="me"
    )
    def current_user(self, request):
        """
        Endpoint to get the currently logged in user
        :param request:
        :return: The current logged in user data
        """
        serializer = self.serializer_class(instance=request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"], detail=False, url_path="resend-registration-code",
        serializer_class=ResendVerificationCodeSerializer
    )
    def resend_registration_code(self, request):
        """ Endpoint to resend registration code """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(data={"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"success": True, "detail": serializer.data}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path="verify", serializer_class=VerifyUserSerializer)
    def verify_user(self, request, pk=None):
        """ Endpoint to verify user """
        serializer = self.serializer_class(data=request.data, context={"email": request.data.get("email")})
        if not serializer.is_valid():
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # Use .is_valid when the serializer is instantiated using the data attribute

        # Initiate a new login for that user
        from rest_framework_simplejwt.tokens import RefreshToken
        email = request.data.get("email")
        user = User.objects.filter(email=email).get()
        refresh = RefreshToken.for_user(user)
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
        return Response(data={'success': True, 'data': token_data}, status=status.HTTP_200_OK)

    @action(
        methods=["POST"], detail=False, url_path="forgot-password",
        serializer_class=ForgotPasswordSerializer
    )
    def resend_reset_code(self, request):
        """ Endpoint to (re)send password reset code """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(data={"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"success": True, "detail": serializer.data}, status=status.HTTP_200_OK)

    @action(
        methods=["POST"], detail=False, url_path="verify-password", serializer_class=VerifyForgotPasswordCodeSerializer
    )
    def verify_password_reset(self, request):
        """ Endpoint to verify password reset """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'success': True}, status=status.HTTP_200_OK)

    @action(
        methods=["POST"], detail=False, url_path="set-password", serializer_class=SetPasswordSerializer
    )
    def set_password(self, request):
        """ Endpoint to set new password """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(data={'success': False, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'success': True}, status=status.HTTP_200_OK)

    @action(
        methods=["POST"], detail=True, url_path="change-password", serializer_class=ChangePasswordSerializer
    )
    def change_password(self, request, pk=None):
        """ Endpoint to change current password """
        user = self.get_object()
        serializer = self.serializer_class(instance=user, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'success': True}, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True, url_path="feedback", serializer_class=ListFeedbackSerializer)
    def user_apps(self, request, pk=None):
        """
        Endpoint that returns the list user's feedback
        :param pk:
        :param request: The HTTPRequest
        :return: List of User's Apps
        """
        user = self.get_object()
        apps_list = FeedbackModel.objects.filter(owner=user.pk)
        # Paginate queryset
        pages = self.paginate_queryset(apps_list)
        if pages is not None:
            serializer = self.serializer_class(apps_list, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(instance=apps_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True, url_path="feedback-suggestion", serializer_class=ListFeedbackSerializer)
    def user_apps_suggestion(self, request, pk=None):
        """
        Endpoint that returns feedback suggestions for a user
        :param pk:
        :param request: The HTTPRequest
        :return: List a suggestion of Apps
        :Howto:
        1. From the list of the user feedback
        2. From the list of tags of the user feedback.
        """
        user = self.get_object()
        apps_list = FeedbackModel.objects.filter(owner=user.pk)
        # Paginate queryset
        pages = self.paginate_queryset(apps_list)
        if pages is not None:
            serializer = self.serializer_class(apps_list, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(instance=apps_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="generate-strong-password",
        serializer_class=GenerateStrongPasswordSerializer
    )
    def generate_strong_password(self, request, pk=None):
        """
        Endpoint to generate strong password
        """
        password = User.objects.make_random_password(12)
        return Response(data=password, status=status.HTTP_200_OK)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        """ Post endpoint for logout functionality """
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as exc:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_205_RESET_CONTENT)
