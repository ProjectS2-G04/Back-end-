import json
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from backend import settings
from .models import PasswordReset, User
from users.groups import add_user_to_group
from .serializers import (
    ChangePasswordSerializer,
    CodeSerializer,
    EmailSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserRegisterSerializer,
    UserSerializer,
)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  
            user.save()
            add_user_to_group(user.email, "Patient")
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_url = request.build_absolute_uri(
                reverse("verify-email", kwargs={"uidb64": uid, "token": token})
            )
            subject = "Verify your email"
            message = f"Click the link below to verify your email:\n{verification_url}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            return Response(
                {
                    "message": "Un lien de vérification a été envoyé à votre adresse email. Veuillez vérifier votre boîte de réception."
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            return JsonResponse({"error": "Invalid token"}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.email_verified = True
            user.save()
            return redirect("http://localhost:5173/home")
        else:
            return JsonResponse({"error": "Token expired or invalid"}, status=400)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Email non trouvé ou mot de passe incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"error": "Votre compte n'est pas encore activé. Veuillez vérifier votre email."}, status=status.HTTP_403_FORBIDDEN)

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
    permission_classes = [AllowAny]

    def get_queryset(self):
        role = self.request.query_params.get("role")
        if role:
            return self.queryset.filter(role=role.upper())
        return self.queryset


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


@api_view(["POST"])
def user_register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "Utilisateur créé avec succès.", "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
