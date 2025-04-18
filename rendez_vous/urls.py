from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    #créer un rendez-vous pour un patient spécifique
    path("create/<int:patient_id>/", CreateRendezVousView.as_view(), name="create-rendezvous"),
    path('demandes/rdv/', demandes_rendez_vous, name='demandes_rdv'),
    path('demandes/annulation/', demandes_annulation, name='demandes_annulation'),
]