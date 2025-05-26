# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Profile
from .serializers import GroupSerializer, MembersSerializer, RegisterAdminSerializer, UserProfileSerializer
from accounts.models import User
from rest_framework.generics import RetrieveAPIView ,UpdateAPIView

class RegisterAdminView(generics.CreateAPIView):
    serializer_class = RegisterAdminSerializer

    def ajouter_utilisateur_au_groupe(self, user, group_name):
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Save user with mapped role

        # Use the original frontend role for group assignment
        frontend_role = request.data.get("role")  # MEDECIN, ASSISTANT_MEDECIN, etc.
        email = serializer.validated_data["email"]

        # Map frontend role to group name
        group_map = {
            "MEDECIN": "Médecin",
            "ASSISTANT_MEDECIN": "Assistant Médecin",
            "DIRECTEUR": "Directeur",
            "PATIENT": "Patient"
        }
        group_name = group_map.get(frontend_role)
        if group_name:
            self.ajouter_utilisateur_au_groupe(user, group_name)

        # Send email verification
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = f"http://localhost:5173/verify-email/{uid}/{token}/"
        subject = "Verify your email"
        message = f"Click the link below to verify your email:\n{verification_url}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response(
            {
                "user": {"email": email, "role": frontend_role},
                "message": "Utilisateur créé avec succès. Veuillez vérifier votre email pour activer votre compte.",
            },
            status=status.HTTP_201_CREATED,
        )

# Rest of the views remain unchanged
class GroupMembersAPIView(APIView):
    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response({"groups": serializer.data}, status=status.HTTP_200_OK)

class ListGroupAPIView(APIView):
    group_name = None 

    def get(self, request):
        try:
            group = Group.objects.get(name=self.group_name)
            members = group.accounts_user_set.all()
            serializer = MembersSerializer(members, many=True)
            return Response(
                {"group": self.group_name, "members": serializer.data},
                status=status.HTTP_200_OK
            )
        except Group.DoesNotExist:
            return Response(
                {"group": self.group_name, "members": []},
                status=status.HTTP_200_OK
            )

class ListAdminAPIView(ListGroupAPIView):
    group_name = "Admin"

class ListMedecinAPIView(ListGroupAPIView):
    group_name = "Médecin"

class ListAssisstantAPIView(ListGroupAPIView):     
    group_name = "Assistant Médecin"

class ListDirecteurAPIView(ListGroupAPIView): 
    group_name = "Directeur"

class ListPatientAPIView(ListGroupAPIView):        
    group_name = "Patient"
    permission_classes = []

class UserProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile, created = Profile.objects.get_or_create(user=user)
        return profile
    

class UpdateUserProfileView(UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile, created = Profile.objects.get_or_create(user=user)
        return profile    