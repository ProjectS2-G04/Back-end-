from django.contrib import admin

from .models import *


# Define the DocumentInline for file uploads
class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1  # Number of empty forms shown by default


# Register DossierMedical with the inline Document model
@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]


# Register DossierMedicalEtudian with the inline Document model
@admin.register(DossierMedicalEtudiant)
class DossierMedicalEtudianAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]


# Register DossierMedicalEnseignant with the inline Document model
@admin.register(DossierMedicalEnseignant)
class DossierMedicalEnseignantAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]


# Register DossierMedicalFonctionnaire with the inline Document model
@admin.register(DossierMedicalFonctionnaire)
class DossierMedicalFonctionnaireAdmin(admin.ModelAdmin):
    inlines = [DocumentInline]


admin.site.register(Depistage)