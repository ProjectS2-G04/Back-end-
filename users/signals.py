from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile 
from accounts.models import User

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile automatically when a new user is created."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the profile whenever the user is updated."""
    instance.profile.save()


""""class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'image']    class UpdateUserProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile, created = Profile.objects.get_or_create(user=user)
        return profile"""    