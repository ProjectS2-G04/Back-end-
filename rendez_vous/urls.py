from django.urls import path
from . import views

urlpatterns = [
    path('demande/create/', views.CreateDemandeRendezVousView.as_view(), name='create-demande'),
    path('demande/<int:demande_id>/confirmer/', views.confirmer_demande, name='confirmer-demande'),
    path('demande/<int:demande_id>/annuler/', views.annuler_demande, name='annuler-demande'),
    path('demande/<int:demande_id>/reporter/', views.reporter_demande, name='reporter-demande'),
]
