from django.urls import path
from .views import (
    DossierMedicalEtudiantView,
    DossierMedicalEnseignantView,
    DossierMedicalATSView,
)

urlpatterns = [
    path(
        "dossiers/etudiants/",
        DossierMedicalEtudiantView.as_view(),
        name="dossiers-etudiants-list",
    ),
    path(
        "dossiers/etudiants/<int:pk>/",
        DossierMedicalEtudiantView.as_view(),
        name="dossiers-etudiants-detail",
    ),
    path(
        "dossiers/enseignants/",
        DossierMedicalEnseignantView.as_view(),
        name="dossiers-enseignants-list",
    ),
    path(
        "dossiers/enseignants/<int:pk>/",
        DossierMedicalEnseignantView.as_view(),
        name="dossiers-enseignants-detail",
    ),
    path("dossiers/ats/", DossierMedicalATSView.as_view(), name="dossiers-ats-list"),
    path(
        "dossiers/ats/<int:pk>/",
        DossierMedicalATSView.as_view(),
        name="dossiers-ats-detail",
    ),
]
