from django.urls import path
from .views import *

urlpatterns = [
    

path('search-enseignant/', DossierMedicalEnseignantSearchView.as_view(), name='search-enseignant'),
path('search-etudiant/', DossierMedicalEtudiantSearchView.as_view(), name='search-enseignant'),
path('search-fonctionnaire/', DossierMedicalFonctionnaireSearchView.as_view(), name='search-enseignant'),
path("etudiants/", DossierMedicalEtudianListView.as_view(), name="etudiants-list"),
path("enseignants/", DossierMedicalEnseignantListView.as_view(), name="enseignants-list"),
path("fonctionnaires/", DossierMedicalFonctionnaireListView.as_view(), name="fonctionnaires-list"),
path("archive/<int:pk>/", ArchiveDossierMedicalView.as_view(), name="archive-dossier"),
path("activate/<int:pk>/", ActivateUserView.as_view(), name="activate-user"),
path("desactivate/<int:pk>/", DesactivateUserView.as_view(), name="desactivate-user"),
















    
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
