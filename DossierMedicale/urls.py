# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *
from .views import (
    ActivateUserView,
    ArchiveDossierMedicalView,
    DesactivateUserView,
    DocumentViewSet,
    DossierMedicalATSView,
    DossierMedicalEnseignantListView,
    DossierMedicalEnseignantSearchView,
    DossierMedicalEnseignantView,
    DossierMedicalEtudianListView,
    DossierMedicalEtudiantSearchView,
    DossierMedicalEtudiantView,
    DossierMedicalFonctionnaireListView,
    DossierMedicalFonctionnaireSearchView,
    DownloadMedicalForm,
    GetUserDossierView,
    consulter_dossier_medical,
    search_DossierMedicalEnseignant,
    search_DossierMedicalEtudian,
    search_DossierMedicalFonctionnaire,
)

router = DefaultRouter()
router.register(r"documents", DocumentViewSet)

urlpatterns = [
    path('search-enseignant/', DossierMedicalEnseignantSearchView.as_view(), name='search-enseignant'),
path('search-etudiant/', DossierMedicalEtudiantSearchView.as_view(), name='search-enseignant'),
path('search-fonctionnaire/', DossierMedicalFonctionnaireSearchView.as_view(), name='search-enseignant'),
path("etudiants/", MedicalEtudianListView.as_view(), name="etudiants-list"),
path("enseignants/", MedicalEnseignantListView.as_view(), name="enseignants-list"),
path("fonctionnaires/",MedicalFonctionnaireListView.as_view(), name="fonctionnaires-list"),
path("archive/<int:pk>/", ArchiveDossierMedicalView.as_view(), name="archive-dossier"),
path("toggle-activation/<int:pk>/", ToggleUserActivationView.as_view(), name="activate-user"),





    path(
        "dossiers/search/etudiant/",
        DossierMedicalEtudiantSearchView.as_view(),
        name="search-etudiant",
    ),
    path(
        "dossiers/search/enseignant/",
        DossierMedicalEnseignantSearchView.as_view(),
        name="search-enseignant",
    ),
    path(
        "dossiers/search/fonctionnaire/",
        DossierMedicalFonctionnaireSearchView.as_view(),
        name="search-fonctionnaire",
    ),
    # Function-based search endpoints
    path(
        "dossiers/search-fn/etudiant/",
        search_DossierMedicalEtudian,
        name="search-fn-etudiant",
    ),
    path(
        "dossiers/search-fn/enseignant/",
        search_DossierMedicalEnseignant,
        name="search-fn-enseignant",
    ),
    path(
        "dossiers/search-fn/fonctionnaire/",
        search_DossierMedicalFonctionnaire,
        name="search-fn-fonctionnaire",
    ),
    # List endpoints
     path(
        "dossiers/etudiants/<int:pk>/",
        DossierMedicalEtudiantView.as_view(),
        name="dossiers-etudiants-detail",
    ),
    path(
        "dossiers/etudiants/",
        DossierMedicalEtudianListView.as_view(),
        name="etudiants-list",
    ),
    path("dossiers/etudiants/create/", DossierMedicalEtudiantView.as_view(), name="dossiers-etudiants-create"),
    path("dossiers/etudiants/", DossierMedicalEtudianListView.as_view(), name="etudiants-list"),
    path("dossiers/etudiants/<int:pk>/", DossierMedicalEtudiantView.as_view(), name="dossiers-etudiants-detail"),
    path(
        "dossiers/enseignants/",
        DossierMedicalEnseignantListView.as_view(),
        name="enseignants-list",
    ),
    path(
        "dossiers/fonctionnaires/",
        DossierMedicalFonctionnaireListView.as_view(),
        name="fonctionnaires-list",
    ),
    path(
        "dossiers/ats/<int:pk>/",
        DossierMedicalATSView.as_view(),
        name="dossiers-ats-detail",
    ),
    # Role-specific dossier endpoints
    path(
        "dossiers/etudiants/<int:pk>/",
        DossierMedicalEtudiantView.as_view(),
        name="dossiers-etudiants-list",
    ),
    path(
        "dossiers/enseignants/<int:pk>/",
        DossierMedicalEnseignantView.as_view(),
        name="dossiers-enseignants-detail",
    ),
   path('dossiers/enseignants/', DossierMedicalEnseignantListView.as_view(), name='enseignants-list'),
# urls.py
path("dossiers/enseignants/create/", DossierMedicalEnseignantView.as_view(), name="dossiers-enseignants-create"),  
   path(
        "dossiers/ats/<int:pk>/",
        DossierMedicalATSView.as_view(),
        name="dossiers-ats-detail",
    ),
    # Generic dossier endpoints
    path("dossiers/", consulter_dossier_medical, name="liste-dossiers"),
    path(
        "dossiers/<int:dossier_id>/", consulter_dossier_medical, name="detail-dossier"
    ),  # Changed pk to dossier_id
    path(
        "dossiers/ats/", DossierMedicalATSView.as_view(), name="dossiers-ats-list"
    ),  ######
    path(
        "dossiers/archive/<int:pk>/",
        ArchiveDossierMedicalView.as_view(),
        name="archive-dossier",
    ),
    path("users/activate/<int:pk>/", ActivateUserView.as_view(), name="activate-user"),
    path(
        "users/desactivate/<int:pk>/",
        DesactivateUserView.as_view(),
        name="desactivate-user",
    ),
    # Download endpoint
    path(
        "dossiers/download/<int:document_id>/",
        DownloadMedicalForm.as_view(),
        name="download-dossier",
    ),
    # User-specific dossier
    path("dossiers/by-user/", GetUserDossierView.as_view(), name="get-user-dossier"),
    # Router for ViewSets
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
