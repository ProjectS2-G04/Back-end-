from django.contrib import admin

from .models import *
admin.site.register(DossierMedical)
admin.site.register(DossierMedicalEtudian)
admin.site.register(DossierMedicalEnseignant)
admin.site.register(DossierMedicalFonctionnaire)
