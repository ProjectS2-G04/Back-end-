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