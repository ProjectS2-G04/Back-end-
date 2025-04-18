from django.urls import  path
from .views import *
from . import views

urlpatterns = [
    path("create/<int:patient_id>/", CreateRendezVousView.as_view(), name="create-rendezvous"),
    path('demandes/rdv/', demandes_rendez_vous, name='demandes_rdv'),
    path('demandes/annulation/', demandes_annulation, name='demandes_annulation'),
    path('demande/create/', views.CreateDemandeRendezVousView.as_view(), name='create-demande'),
    path('demande/<int:demande_id>/confirmer/', views.confirmer_demande, name='confirmer-demande'),
    path('demande/<int:demande_id>/annuler/', views.annuler_demande, name='annuler-demande'),
    path('demande/<int:demande_id>/reporter/', views.reporter_demande, name='reporter-demande'),
]


