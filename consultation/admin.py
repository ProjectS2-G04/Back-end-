from django.contrib import admin
from .models import Consultation, MaladieContagieuse, MaladieCronique
# Register your models here.
admin.site.register(Consultation)
admin.site.register(MaladieContagieuse)
admin.site.register(MaladieCronique)