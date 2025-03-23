from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import *


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image=models.ImageField(upload_to='profile_pics'  ,default='profile_pics/image.jpg')
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
    
def validate_esi_sba_email(value):

    if not value.endswith("@esi-sba.dz"):
        raise ValidationError("Email must end with '@esi-sba.dz'.")    
    
    

