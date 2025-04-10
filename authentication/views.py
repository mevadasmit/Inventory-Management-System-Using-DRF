from django.contrib.auth import get_user_model
from rest_framework import generics, status, mixins, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from authentication.models import CustomUser
from authentication.serializers import UserRegisterSerializer, LoginSerializer, ForgotPasswordSerializer, \
    PasswordResetSerializer, ChangePasswordSerializer, ProfileSerializer
from authentication.permissions import IsOwnerOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from base.role_access import RoleBasedPermission
from base.constants import (FIELD_ADMIN, FIELD_IM)
from authentication.constants import (USER_CREATED_SUCCESS, USER_REGISTRATION_FAILED, USER_LOGGED_IN, USER_LOGIN_FAILED,
                                      FORGOT_PASSWORD_FAILED, PASSWORD_RESET_FAILED, CHANGE_PASSWORD_FAILED,
                                      USER_LOGGED_OUT, ALREADY_USER_LOGGED_OUT, PROFILE_UPDATE_FAILED,
                                      PROFILE_UPDATE_SUCCESS, PROFILE_FETCH_SUCCESSFULLY)
from main_admin.utils import success_response, error_response

user = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API view for Admin to create a new user.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles user creation and returns a success response.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
            return success_response(serializer.data, USER_CREATED_SUCCESS , status.HTTP_201_CREATED)
        return error_response(serializer.errors, USER_REGISTRATION_FAILED, status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    Logs in an existing user.

    This view handles user login by validating provided credentials using the LoginSerializer.
    Upon successful login, user data and a token are returned.
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """
            Logs in a user.

            Args:
                request: The incoming request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments.

            Returns:
                Response: A response object containing user data and token upon successful login.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return success_response(USER_LOGGED_IN, serializer.data, status.HTTP_200_OK)
        return error_response(serializer.errors, USER_LOGIN_FAILED, status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(generics.GenericAPIView):
    """
        Handles the forgot password request.

        This view utilizes the ForgotPasswordSerializer to initiate the password reset process.
        Upon successful validation, a password reset email is sent to the user.
    """
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        """
            Initiates the password reset process.

            Args:
                request: The incoming request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments.

            Returns:
                Response: A response object indicating the password reset email sent status.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return error_response(serializer.errors, FORGOT_PASSWORD_FAILED, status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
        Confirms the password reset and updates the user's password.

        This view uses the PasswordResetSerializer to validate the new password and token,
        and then saves the new password for the user.
    """
    queryset = CustomUser.objects.all()
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        """
            Handles the password reset confirmation.

            Args:
                request: The incoming request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments.

            Returns:
                Response: A response object indicating the password reset status.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return error_response(serializer.errors, PASSWORD_RESET_FAILED, status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """
        Handles the change password request.

        This view uses the ChangePasswordSerializer to validate and update the user's password.
        Only authenticated users can access this view.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def post(self, request, *args, **kwargs):
        """
            Changes the password for the authenticated user.

            Args:
                request: The incoming request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments.

            Returns:
                Response: A response object indicating the password change status.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return error_response(serializer.errors, CHANGE_PASSWORD_FAILED, status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(generics.GenericAPIView):
    """
    Logs out the current user by blacklisting their refresh tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return error_response("Refresh token is required.", ALREADY_USER_LOGGED_OUT, status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response(USER_LOGGED_OUT, status_code=status.HTTP_200_OK)
        except Exception as e:
            return error_response(str(e), ALREADY_USER_LOGGED_OUT, status.HTTP_400_BAD_REQUEST)



class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
        Updates the user profile.

        This view allows authenticated users to retrieve and update their profile information
        using the ProfileSerializer. Partial updates are supported.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile  # noqa

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data, PROFILE_FETCH_SUCCESSFULLY, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
            Updates the user profile.

            Args:
                request: The incoming request object.
                *args: Additional positional arguments.
                **kwargs: Additional keyword arguments.

            Returns:
                Response: A response object containing the updated profile data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return success_response(serializer.data, PROFILE_UPDATE_SUCCESS, status.HTTP_200_OK)
        return error_response(serializer.errors, PROFILE_UPDATE_FAILED, status.HTTP_400_BAD_REQUEST)
