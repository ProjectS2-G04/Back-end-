from django.contrib import admin
from .models import RendezVous, DemandeRendezVous, PlageHoraire, Ordonnance, Medicament

admin.site.register(RendezVous)
admin.site.register(DemandeRendezVous)
admin.site.register(PlageHoraire)
admin.site.register(Ordonnance)
admin.site.register(Medicament)