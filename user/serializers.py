import re

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
# from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from timeline.models import TimelineModel
from user.models import User, AccountCodeModel
from user.tasks import send_new_user_email
from user.utils import RegistrationCode, generate_and_send_email_code


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': gettext_lazy('No active account with this credentials.'),
        'authentication': gettext_lazy('User credentials inactive.')
    }

    @classmethod
    def get_token(cls, user):
        if not user.is_active:
            raise AuthenticationFailed(
                gettext_lazy("User credentials declined."), code="authentication"
            )
        # if not user.is_verified:
        #     raise AuthenticationFailed(
        #         gettext_lazy("Account not yet verified."), code="not_verified"
        #     )

        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)

        # Custom claims on the jwt token
        token.id = user.id
        token['dp'] = user.dp.url if user.dp else None
        token['email'] = user.email
        token['firstname'] = user.firstname
        token['lastname'] = user.lastname
        token['is_verified'] = user.is_verified
        user.save_last_login()
        return token


class SignupSerializer(serializers.ModelSerializer):
    """
    The Signup Serializer
    """
    queryset = User.objects.all()
    fullname = serializers.CharField()
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=queryset, message="Email must be unique", lookup="iexact")]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "firstname", "lastname", "password"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        fullname = attrs.get('fullname')
        email = attrs.get('email')
        phone_no = attrs.get('phone_no')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        gender = attrs.get('gender')

        if password := password.strip():
            if len(password) < 8:
                raise serializers.ValidationError({"password": "Password cannot be less than 8 chars"})
            elif not re.match(r'[A-Za-z0-9_@]{8,}', password):
                raise serializers.ValidationError({"password": "Password must contain a number, a symbol and no spaces"})
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Oops. Passwords do not match."})
        if gender not in ["MALE", "FEMALE"]:
            raise serializers.ValidationError({"gender": "Accepted gender choices are Male or Female"})
        if phone_no := phone_no.strip():
            if len(phone_no) > 17:
                raise serializers.ValidationError({"phone_no": "Invalid Phone number"})
            elif not re.match(r'\d{11,17}', phone_no):
                raise serializers.ValidationError({"phone_no": "Invalid phone number, Kindly confirm the digits"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        fullname = validated_data.get("fullname")

        # Get firstname and lastname from fullname
        fullname_split = fullname.split(" ", 1)
        first_name = fullname.split(" ")[0]
        last_name = fullname.split(" ")[-1] if len(fullname_split) > 1 else ""

        # Get the other validated data
        email = validated_data.get("email")
        password = validated_data.get("password")
        phone_no = validated_data.get("phone_no")
        gender = validated_data.get("gender")
        country = validated_data.get("country")

        # Create the user
        new_user = self.Meta.model.objects.create_user(
            email=email, password=password, first_name=first_name, last_name=last_name,
            phone_no=phone_no, gender=gender, country=country, is_active=True
        )
        return validated_data


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # print(instance.dp.url)
        # if instance.dp and not instance.dp.url.startswith("http"):
        #     request = self.context.get("request")
        #     data["dp"] = request.META.get("HTTP_REFERER").split(":")[0]+"://"+request.get_host()+instance.dp
        # data["social_account_dict"] = [instance.social_account_dict]
        return data


class CreateUserSerializer(serializers.ModelSerializer):
    """
    The Create User Serializer
    """
    queryset = User.objects.all()
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=queryset, message="Email must be unique", lookup="iexact")]
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "id", "email", "firstname", "lastname", "password"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        firstname = attrs.get('firstname')
        lastname = attrs.get('lastname')
        email = attrs.get('email')
        password = attrs.get('password')

        if password := password.strip():
            if len(password) < 8:
                raise serializers.ValidationError({"error": "Password cannot be less than 8 chars"}, "password")
            # elif not re.match(r'[A-Za-z0-9_@]{8,}', password):
            #     raise serializers.ValidationError(
            #         {"error": "Password must contain a number, a symbol and no spaces"},
            #         "password"
            #     )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        from cryptography.fernet import Fernet
        firstname = validated_data.get("firstname")
        lastname = validated_data.get("lastname")

        # Get the other validated data
        email = validated_data.get("email")
        password = validated_data.get("password")

        key = Fernet.generate_key()
        # cipher = Fernet(key)
        # TODO: The cipher could be used to recycle each users once per year. Meaning that the cipher will be
        #  regenerated for every user once per year.

        # Create the user
        # The key is a unique identifier for users
        new_user = self.Meta.model.objects.create_user(
            eid=key.decode("utf-8"), email=email, password=password,
            firstname=firstname, lastname=lastname, is_active=True
        )
        new_user.update_last_resend_datetime()

        user_reg_code = generate_and_send_email_code(new_user)
        # Create the CodeModel and save
        AccountCodeModel.objects.create(user=new_user, reg_code=user_reg_code)
        # Create the TimelineModel
        TimelineModel.objects.create_user_timeline(user_id=new_user.id,category="SIGNUP")
        return new_user


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "Kindly create an account first"}, "not_exist")
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        user = User.objects.get(email=email)
        user.update_last_resend_datetime()

        user_reg_code = generate_and_send_email_code(user)
        # Update the CodeModel
        AccountCodeModel.objects.filter(user=user).update(reg_code=user_reg_code, updated_at=timezone.now())
        return validated_data


class VerifyUserSerializer(serializers.Serializer):
    """
    Endpoint to verify user serializer
    """
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        # 1.    Get the code sent to the user
        # 2.    Verify that the code is the same as the code saved on the user
        # 3.    Verify that the code is not expired.
        code = attrs.get("code")
        if not code:
            raise serializers.ValidationError({"error": "Unable to retrieve verification code."}, "empty")
        if len(code) != 8:
            raise serializers.ValidationError({"error": "Code is invalid. Confirm the code we sent to you."}, "invalid")
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        code = validated_data.get("code")
        code = code.lower()
        code_filter_obj = AccountCodeModel.objects.filter(reg_code=code)
        if not code_filter_obj.exists():
            raise serializers.ValidationError(
                {"error": "Unable to verify code. Kindly regenerate the code."},
                "not_exist"
            )
        code_obj = code_filter_obj.get()
        code_verification_status = RegistrationCode.verify(
            raw_data=code_obj.user.email+str(code_obj.user.last_resend_code_datetime),
            enc_key=code_obj.user.eid, signed_data=code
        )
        if not code_verification_status:
            raise serializers.ValidationError({"error": "Code is invalid"}, "invalid")
        if timezone.now() - code_obj.updated_at > timezone.timedelta(minutes=5):
            raise serializers.ValidationError({"error": "Code is expired"}, "expired")
        user = User.objects.filter(email=code_obj.user.email).get()
        if user.is_verified:
            raise serializers.ValidationError({"error": "Cannot verify an already verified user"}, "unverified")
        user.is_verified = True
        user.save()
        code_obj.delete()

        # Create the TimelineModel on successful verification
        TimelineModel.objects.create_user_timeline(user_id=user.id, category="ACCOUNT_VERIFIED")

        # Perform login operation for that user.
        # from rest_framework_simplejwt.tokens import RefreshToken
        
        # def get_tokens_for_user(user):
        # refresh = RefreshToken.for_user(user)
        # return {
        #     'refresh': str(refresh),
        #     'access': str(refresh.access_token),
        # }
        # refresh = RefreshToken.for_user(user)
        # token_data = {
        #     # "user": user,
        #     "refresh": str(refresh),
        #     "access": str(refresh.access_token)
        # }
        # validated_data["token_data"] = token_data
        # print(validated_data)
        # return user
        # return data
        return validated_data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        if not User.objects.filter(email=email, is_active=True).exists():
            raise serializers.ValidationError(
                {"error": "Password cannot be reset. Kindly activate your account."},
                "inactive"
            )
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "Kindly create an account first"}, "not_exist")
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        user = User.objects.get(email=email)
        user.update_last_resend_datetime()

        user_reset_code = generate_and_send_email_code(user, email_type="RESET")
        # Update or Create the CodeModel
        AccountCodeModel.objects.update_or_create(user=user, reset_code=user_reset_code, updated_at=timezone.now())
        return validated_data


class VerifyForgotPasswordCodeSerializer(serializers.Serializer):
    """
    Serializer to verify forgot password code
    """
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        # 1.    Get the code sent to the user
        # 2.    Verify that the code is the same as the code saved on the user
        # 3.    Verify that the code is not expired.
        super().validate(attrs)
        code = attrs.get("code")
        if not code:
            raise serializers.ValidationError({"error": "Unable to retrieve verification code."}, "empty")
        if len(code) != 8:
            raise serializers.ValidationError({"error": "Code is invalid. Confirm the code we sent to you."}, "invalid")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        code = validated_data.get("code")
        email = validated_data.get("email")
        code = code.lower()
        user = User.objects.filter(email=email).first()
        code_filter_obj = AccountCodeModel.objects.filter(user=user, reset_code=code)
        if not code_filter_obj.exists():
            raise serializers.ValidationError(
                {"error": "Unable to verify code. Kindly regenerate the code."},
                "not_exist"
            )
        code_obj = code_filter_obj.get()
        code_verification_status = RegistrationCode.verify(
            raw_data=code_obj.user.email+str(code_obj.user.last_resend_code_datetime),
            enc_key=code_obj.user.eid, signed_data=code
        )
        if not code_verification_status:
            raise serializers.ValidationError({"error": "Code is invalid"}, "invalid")
        if timezone.now() - code_obj.updated_at > timezone.timedelta(minutes=5):
            raise serializers.ValidationError({"error": "Reset code has expired. Generate a new code"}, "expired")
        # Set an unusable password for the user, so the user can no longer login with the previous password
        code_obj.user.set_unusable_password()
        code_obj.user.save()
        code_obj.delete()
        return validated_data


class SetPasswordSerializer(serializers.Serializer):
    """
    Serializer to set new password
    """
    queryset = User.objects.filter(is_active=True, is_verified=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=queryset, message="Email must be unique", lookup="iexact")]
    )
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True, validators=[validate_password]
    )

    def validate(self, attrs):
        super().validate(attrs)
        email = attrs.get("email")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password := password.strip():
            if len(password) < 8:
                raise serializers.ValidationError({"error": "Password cannot be less than 8 chars"}, "password")
            # elif not re.match(r'[A-Za-z0-9_@]{8,}', password):
            #     raise serializers.ValidationError(
            #         {"password": "Password must contain a number, a symbol and no spaces"}
            #     )
        if password != confirm_password:
            raise serializers.ValidationError({"error": "Oops. Passwords do not match."}, "confirm_password")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        confirm_password = validated_data.get("confirm_password")

        email = email.lower()
        user_obj = self.queryset.filter(email=email)
        # code_filter_obj = AccountCodeModel.objects.filter(user=user_obj, reset_code__isnull=False)
        # if not code_filter_obj.exists():
        #     raise serializers.ValidationError({
        #         "not_exist": "Unable to verify reset code. Kindly re-initiate password reset"
        #     })
        # code_obj = code_filter_obj.get()
        # code_verification_status = RegistrationCode.verify(
        #     raw_data=code_obj.user.email+str(code_obj.user.last_resend_code_datetime),
        #     enc_key=code_obj.user.eid, signed_data=code_obj.reset_code
        # )
        # if not code_verification_status:
        #     raise serializers.ValidationError({"invalid": "Code is invalid"})
        # if timezone.now() - code_obj.created_at > timezone.timedelta(minutes=5):
        #     raise serializers.ValidationError({"expired": "Code is expired"})
        # user = User.objects.filter(email=code_obj.user.email).get()
        # if user.is_verified:
        #     raise serializers.ValidationError({"user": "User already verified. Cannot complete operation"})
        # user.is_verified = True
        user = user_obj.get()
        user.set_password(password)
        user.save()
        # code_obj.delete()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer to change new password
    """
    current_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True, validators=[validate_password]
    )

    def validate(self, attrs):
        super().validate(attrs)
        user = self.instance
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")

        if not user.check_password(current_password):
            raise serializers.ValidationError({"error": "This is not your current password"}, "invalid")
        if new_password := new_password.strip():
            if len(new_password) < 8:
                raise serializers.ValidationError(
                    {"error": "Password cannot be less than 8 chars"},
                    "new_password"
                )
            # elif not re.match(r'[A-Za-z0-9_@]{8,}', new_password):
            #     raise serializers.ValidationError(
            #         {"new_password": "Password must contain a number, a symbol and no spaces"}
            #     )
        if current_password == new_password:
            raise serializers.ValidationError({"error": "The Passwords cannot be the same"}, "new_password")
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        user = instance
        new_password = validated_data.get("new_password")
        user.set_password(new_password)
        user.save()
        return user


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Current User Serializer
    """
    class Meta:
        model = User
        fields = []


class GenerateStrongPasswordSerializer(serializers.Serializer):
    """
    Generate Strong Password Serializer
    """
    password = serializers.CharField()
