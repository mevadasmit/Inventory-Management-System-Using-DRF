from django.utils.crypto import get_random_string
from rest_framework import serializers
from authentication.models import CustomUser, Profile
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from base.utils import send_registration_email, send_password_reset_email
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from authentication.constants import (CREDENTIAL_ERROR, BOTH_FILED_REQUIRED, INVALID_EMAIL, FORGOT_MAIL_SANDED,
                                      PASSWORD_NOT_MATCH, TOKEN_REQUIRED, INVALID_TOKEN, PASSWORD_RESET_SUCCESS,
                                      ALL_PASSWORD_REQUIRED, NEW_OLD_PASSWORD_NOT_MATCH, INVALID_OLD_PASSWORD,
                                      USER_UN_AUTHENTICATED, )
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import serializers

user = get_user_model()
token_generator = PasswordResetTokenGenerator()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    Handles user creation with a randomly generated password
    and sends a registration email to the user.
    """

    class Meta:
        model = CustomUser
        fields = ['id','first_name', 'last_name', 'email', 'role', 'phone_number', "created_by", "updated_by"]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_by": {"read_only": True},
            "updated_by": {"read_only": True}
        }

    def create(self, validated_data):
        """
        Create a new user instance with a random password and send an email.

        Args:
            validated_data (dict): Validated user data.

        Returns:
            CustomUser: Newly created user instance.
        """
        random_password = get_random_string(10)

        validated_data.update({
            "is_first_time_login": True,
        })

        users = CustomUser.objects.create(**validated_data)
        users.set_password(random_password)
        users.save()

        send_registration_email(users, random_password)

        return users


class LoginSerializer(serializers.Serializer):
    """
        Serializer for user login.
        This serializer handles user authentication by validating provided email
        and password against existing users.
        A new authentication token is generated if the credentials are valid.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
            Validate the provided email and password.

            Args:
                data (dict): The data containing email and password.

            Returns:
                dict: A dictionary containing the authenticated user and token.

            Raises:
                serializers.ValidationError: If email or password are invalid.
        """
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError(BOTH_FILED_REQUIRED)

        users = authenticate(request=self.context.get("request"), username=email, password=password)

        if not users:
            raise serializers.ValidationError(CREDENTIAL_ERROR)

        refresh = RefreshToken.for_user(users)


        return {
            "user": users,
            "refresh": str(refresh),
            "access":str(refresh.access_token)
        }


    def to_representation(self, instance):
        user = instance['user']
        return {
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "role": user.role
            },
            "access": instance["access"],
            "refresh": instance["refresh"]
        }
        
class ForgotPasswordSerializer(serializers.Serializer):
    """
        Serializer for initiating the password reset process.
        This serializer validates the provided email address and, if valid
        sends a password reset email containing a unique token to the user.
    """
    email = serializers.EmailField()

    @staticmethod
    def validate_email(value):
        """
            Validate the provided email address.
            Args:
                value (str): The email address to validate.
            Returns:
                str: The validated email address.
            Raises:
                serializers.ValidationError: If the email address is not found.
        """
        try:
            CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist as e:
            raise serializers.ValidationError(INVALID_EMAIL) from e
        return value

    def save(self, **kwargs):
        """
            Send a password reset email to the user.

            Retrieves the user associated with the validated email address
            and sends a password reset email containing a unique token.

            Returns:
                dict: A dictionary containing a success message and the generated token.
        """
        email = self.validated_data['email']
        users = CustomUser.objects.get(email=email)
        token = send_password_reset_email(users, request=self.context.get('request'))
        return {"message": FORGOT_MAIL_SANDED, "token": token}


class PasswordResetSerializer(serializers.Serializer):
    """
        Serializer for resetting a user's password.

        This serializer validates the provided new password and confirmation,
        checks the validity of the provided token, and updates the user's password.
    """
    new_password = serializers.CharField(write_only=True, max_length=15)
    confirm_password = serializers.CharField(write_only=True, max_length=15)

    def validate(self, data):  # sourcery skip: use-next
        """
            Validate the provided data and token.

            Args:
                data (dict): The data containing the new password and confirmation.

            Returns:
                dict: The validated data.

            Raises:
                serializers.ValidationError: If passwords don't match or the token is invalid.
        """
        request = self.context.get('request')
        token = request.query_params.get('token') if request else None

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(PASSWORD_NOT_MATCH)

        if not token:
            raise serializers.ValidationError(TOKEN_REQUIRED)

        users = None

        for potential_user in CustomUser.objects.filter(is_active=True):
            if token_generator.check_token(potential_user, token):
                users = potential_user
                break

        if not users:
            raise serializers.ValidationError(INVALID_TOKEN)

        self.user = users
        return data

    def save(self, **kwargs):
        """
            Save the new password for the user.

            Sets the user's password to the validated new password and saves the user object.

            Returns:
                dict: A dictionary containing a success message.
        """
        new_password = self.validated_data['new_password']
        users = self.user
        users.set_password(new_password)
        users.save()
        return {"message": PASSWORD_RESET_SUCCESS}


class ChangePasswordSerializer(serializers.Serializer):
    """
        Serializer for changing a user's password.

        This serializer validates the provided old password, new password, and confirmation,
        and updates the user's password if all validations pass.
    """
    old_password = serializers.CharField(write_only=True, max_length=15)
    new_password = serializers.CharField(write_only=True, max_length=15)
    confirm_password = serializers.CharField(write_only=True, max_length=15)

    def validate(self, data):
        """
            Validate the provided data.

            Args:
                data (dict): The data containing the old password, new password and confirmation.

            Returns:
                dict: The validated data.

            Raises:
                serializers.ValidationError: If passwords don't match or the old password is invalid.
        """
        users = self.context["request"].user

        if not users.is_authenticated:
            raise serializers.ValidationError(USER_UN_AUTHENTICATED)

        if not data["old_password"] or not data["new_password"] or not data["confirm_password"]:
            raise serializers.ValidationError(ALL_PASSWORD_REQUIRED)

        if not users.check_password(data["old_password"]):
            raise serializers.ValidationError(INVALID_OLD_PASSWORD)

        if data["confirm_password"] != data["new_password"]:
            raise serializers.ValidationError(NEW_OLD_PASSWORD_NOT_MATCH)

        return data

    def save(self, **kwargs):
        """
            Save the new password for the user.

            Sets the user's password to the validated new password and saves the user object.

            Returns:
                dict: A dictionary containing a success message.
        """
        users = self.context["request"].user
        new_password = self.validated_data['new_password']
        users.set_password(new_password)
        users.save()
        return {"message": PASSWORD_RESET_SUCCESS}


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for the CustomUser model.

        This serializer provides a way to serialize and deserialize instances
        of the CustomUser model, including fields like first name, last name,
        email, and phone number.
    """

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "role", "email", "phone_number", "created_by", "updated_by"]
        extra_kwargs = {'role': {'read_only': True},
                        "email": {"required": False},
                        "phone_number": {"required": False},
                        "created_by": {"read_only": True, "required": False},
                        "updated_by": {"read_only": True, "required": False}}


class ProfileSerializer(serializers.ModelSerializer):
    """
        Serializer for the Profile model.

        This serializer handles the serialization and deserialization of Profile instances,
        including the related UserSerializer for nested user data updates.
    """

    user = UserSerializer(partial=True)

    class Meta:
        model = Profile
        fields = ["bio", "image", "user"]

    def update(self, instance, validated_data):
        # Handle nested user update
        if "user" in validated_data:
            user_data = validated_data.pop("user")
            user_instance = instance.user
            for attr, value in user_data.items():
                if value is not None:  # Update only if value is provided
                    setattr(user_instance, attr, value)
            user_instance.save()

        # Update only provided profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
