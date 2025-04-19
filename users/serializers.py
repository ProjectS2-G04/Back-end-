from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import Group
from accounts.models import User





# users/serializers.py
from rest_framework import serializers
from accounts.models import User

class RegisterAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=['MEDECIN', 'ASSISTANT_MEDECIN', 'DIRECTEUR', 'PATIENT'], required=True
    )

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "role"]

    # Map frontend roles to backend User model roles
    ROLE_MAPPING = {
        'MEDECIN': 'DOCTOR',
        'ASSISTANT_MEDECIN': 'ASSISTANT',
        'DIRECTEUR': 'DIRECTOR',
        'PATIENT': 'PATIENT'
    }

    def validate(self, data):
        email = data.get("email")
        role = data.get("role")

        # Validate email domain
        if not email.endswith("@esi-sba.dz"):
            raise serializers.ValidationError(
                {"email": "Seules les adresses email avec le domaine @esi-sba.dz sont autorisées."}
            )

        # Validate role and map to backend role
        if role not in ['MEDECIN', 'ASSISTANT_MEDECIN', 'DIRECTEUR', 'PATIENT']:
            raise serializers.ValidationError(
                {"role": "Le rôle doit être 'MEDECIN', 'ASSISTANT_MEDECIN', 'DIRECTEUR' ou 'PATIENT'."}
            )

        # Map the role to the backend value for storage
        data['role'] = self.ROLE_MAPPING[role]
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=validated_data["role"],  # Use mapped role (DOCTOR, ASSISTANT, etc.)
            is_active=False,  # Require email verification
            email_verified=False
        )
        return user



























class AddUserToGroupSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def __init__(self, *args, **kwargs):
        """Accept group_name dynamically from the view"""
        self.group_name = kwargs.pop("group_name", None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        """Validate if user and group exist before adding."""
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"user_email": f"❌ L'utilisateur avec l'email '{data['email']}' n'existe pas."}
            )
        try:
            group = Group.objects.get(name=self.group_name)
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                {"group_name": f"❌ Le groupe '{self.group_name}' n'existe pas."}
            )
        data["user"] = user
        data["group"] = group
        return data

    def save(self):
        """Add user to the group, avoiding duplicates."""
        user = self.validated_data["user"]
        group = self.validated_data["group"]

        if user.groups.filter(id=group.id).exists():
            raise serializers.ValidationError(
                {"message": f"⚠️ L'utilisateur '{user.email}' est déjà membre du groupe '{group.name}'."}
            )
        user.groups.add(group)



class RemoveUserFromGroupSerializer(serializers.Serializer): 
    user_email = serializers.EmailField()
    group_name = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["user_email"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"user_email": f"⚠️ L'utilisateur avec l'email '{data['user_email']}' n'existe pas."}
            )

        try:
            group = Group.objects.get(name=data["group_name"])
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                {"group_name": f"⚠️ Le groupe '{data['group_name']}' n'existe pas."}
            )

        if not user.groups.filter(id=group.id).exists():
            raise serializers.ValidationError(
                {"group_name": f"⚠️ L'utilisateur '{data['user_email']}' n'appartient pas au groupe '{data['group_name']}'."}
            )

        data["user"] = user
        data["group"] = group
        return data

    def save(self):
        user = self.validated_data["user"]
        group = self.validated_data["group"]
        user.groups.remove(group)

class RemoveUserFromGroupSerializer(serializers.Serializer): 
    user_email = serializers.EmailField()
    group_name = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["user_email"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"user_email": f"L'utilisateur avec l'email '{data['user_email']}' n'existe pas."}
            )

        try:
            group = Group.objects.get(name=data["group_name"])
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                {"group_name": f"Le groupe '{data['group_name']}' n'existe pas."}
            )

        if not user.groups.filter(id=group.id).exists():
            raise serializers.ValidationError(
                {"group_name": f"L'utilisateur '{data['user_email']}' n'appartient pas au groupe '{data['group_name']}'."}
            )

        data["user"] = user
        data["group"] = group
        return data

    def save(self):
        user = self.validated_data["user"]
        group = self.validated_data["group"]
        user.groups.remove(group)










class MembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email' , "sub_role"]

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
         model =Group
         fields = ['id' , "name"]


class UserUpadateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name' ,required=False)
    last_name = serializers.CharField(source='user.last_name' , required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image']

    def update(self, instance, validated_data):
        
        user_data = validated_data.pop('user', {})
        user = instance.user
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.save()

        
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
    


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image']    