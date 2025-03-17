import json
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from backend import settings

from .models import PasswordReset, User
from .serializers import (
    ChangePasswordSerializer,
    CodeSerializer,
    EmailSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserSerializer,
    UserRegisterSerializer
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": UserSerializer(user).data,
                "message": "Utilisateur créé avec succès.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Mot de passe incorrect ou email non trouvé.")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "access": access_token,
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Mot de passe mis à jour avec succès."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendResetCodeView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                reset = PasswordReset.objects.create(
                    user=user,
                    expires_at=timezone.now() + timezone.timedelta(minutes=15),
                )
                send_mail(
                    "Password Reset Code",
                    f"Your reset code is: {reset.code}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return Response({"message": "Reset code sent."})
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
        return Response(serializer.errors, status=400)


class VerifyResetCodeView(APIView):
    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            try:
                reset = PasswordReset.objects.get(code=code)
                if reset.is_expired():
                    return Response({"error": "Code has expired."}, status=400)
                return Response({"message": "Code verified."})
            except PasswordReset.DoesNotExist:
                return Response({"error": "Invalid code."}, status=400)
        return Response(serializer.errors, status=400)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            code = request.data.get("code")

            try:
                reset = PasswordReset.objects.get(code=code)
                if reset.is_expired():
                    return Response({"error": "Code has expired."}, status=400)

                user = reset.user
                user.set_password(serializer.validated_data["password"])
                user.save()
                reset.delete()
                return Response({"message": "Password reset successfully."})
            except PasswordReset.DoesNotExist:
                return Response({"error": "Invalid code."}, status=400)

        return Response(serializer.errors, status=400)

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # 👈 Makes the API public

    def get_queryset(self):
        role = self.request.query_params.get("role")
        if role:
            return self.queryset.filter(role=role.upper())  # Case-insensitive filter
        return self.queryset



class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]



@api_view(['POST'])
def user_register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "Utilisateur créé avec succès.", "user": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)