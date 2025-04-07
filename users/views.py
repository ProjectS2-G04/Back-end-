from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .serializers import UserProfileSerializer
from rest_framework.generics import RetrieveUpdateAPIView

from django.contrib.auth.models import Group
from rest_framework import viewsets ,generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *





class RegisterAdminView(generics.CreateAPIView):
    serializer_class = RegisterAdminSerializer

    def ajouter_utilisateur_au_groupe(self, user, group_name):
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # ✅ Save user first

        role = serializer.validated_data["role"]  # ✅ Use validated data
        email = serializer.validated_data["email"]

        # ✅ Add user to the correct group
        if role == "DIRECTEUR":
            self.ajouter_utilisateur_au_groupe(user, "Directeur")
        elif role == "ASSISTANT_MEDECIN":
            self.ajouter_utilisateur_au_groupe(user, "Assistant Médecin")
        elif role == "MEDECIN":
            self.ajouter_utilisateur_au_groupe(user, "Médecin")
        elif role == "PATIENT":
            self.ajouter_utilisateur_au_groupe(user, "Patient")    

        return Response(
            {
                "user": {"email": email, "role": role},
                "message": "Utilisateur créé avec succès.",
            },
            status=status.HTTP_201_CREATED,
        )

class GroupMembersAPIView(APIView):

    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)  # Correct serializer usage
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
                {"group": self.group_name, "members": []},  # Return empty list
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
        



class UpdateUserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
     user = self.request.user
     profile, created = Profile.objects.get_or_create(user=user)  # Create profile if missing
     return profile
