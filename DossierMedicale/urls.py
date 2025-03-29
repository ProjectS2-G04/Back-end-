from django.urls import path
from .views import *

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
    path('search/etudiant/', 
         search_DossierMedicalEtudian, 
         name='search-etudiant'
         ),
    path('search/enseignant/',
         search_DossierMedicalEnseignant, 
         name='search-enseignant'
         ),
    path('search/fonctionnaire/', 
         search_DossierMedicalFonctionnaire, 
         name='search-fonctionnaire'
         ),
    path('dossiers/',
         consulter_dossier_medical,
         name='liste-dossiers'
         ),
    path('dossiers/<int:dossier_id>/',
         consulter_dossier_medical, 
         name='detail-dossier'
         ),

]
