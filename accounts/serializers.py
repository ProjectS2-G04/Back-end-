import re

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import PasswordReset

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "sub_role",
            "is_active",
            "email_verified",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    sub_role = serializers.ChoiceField(
        choices=["ETUDIANT", "ENSEIGNANT", "ATS"], required=True
    )

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "sub_role"]

    def validate_email(self, value):

        if not re.match(r"^[a-zA-Z]+\.[a-zA-Z]+@esi-sba\.dz$", value):
            raise serializers.ValidationError(
                "Email must be in the format: nom.prenom@esi-sba.dz"
            )
        return value

    def validate_sub_role(self, value):

        value = value.upper()
        if value not in ["ETUDIANT", "ENSEIGNANT", "ATS"]:
            raise serializers.ValidationError(
                "Le rôle doit être l'un des suivants : ETUDIANT, ENSEIGNANT, ATS"
            )
        return value

    def validate(self, data):

        # sub_role = data.get("sub_role")
        # if sub_role == "ETUDIANT":
        #     data["role"] = "ETUDIANT"
        # elif sub_role == "ENSEIGNANT":
        #     data["role"] = "ENSEIGNANT"
        # elif sub_role == "ATS":
        #     data["role"] = "ATS"
        data["role"] = "PATIENT"

        return data

    def create(self, validated_data):
        if User.objects.filter(email=validated_data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "This email is already registered."}
            )

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=validated_data["role"],
            sub_role=validated_data["sub_role"],
        )
        user.is_active = True
        user.save()
        return user


class RegisterAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("L'utilisateur n'existe pas.")

        if not user.is_active:
            raise serializers.ValidationError("Le compte utilisateur est inactif.")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Identifiants incorrects.")

        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not re.match(r"^[a-z]+(\.[a-z]+)+@esi-sba\.dz$", value):
            raise serializers.ValidationError(
                "Email must be in the format: nom.prenom@esi-sba.dz"
            )
        return value


class CodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)


class PasswordResetSerializer(serializers.Serializer):

    code = serializers.CharField(max_length=6, required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Le mot de passe actuel est incorrect.")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError:
            raise serializers.ValidationError(
                "Le mot de passe ne répond pas aux critères de sécurité."
            )
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user
