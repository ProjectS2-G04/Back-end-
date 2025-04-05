from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import *


router = DefaultRouter()
router.register(r'documents', DocumentViewSet)

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
    path("search/etudiant/", search_DossierMedicalEtudian, name="search-etudiant"),
    path(
        "search/enseignant/", search_DossierMedicalEnseignant, name="search-enseignant"
    ),
    path(
        "search/fonctionnaire/",
        search_DossierMedicalFonctionnaire,
        name="search-fonctionnaire",
    ),
    path("dossiers/", consulter_dossier_medical, name="liste-dossiers"),
    path(
        "dossiers/<int:dossier_id>/", consulter_dossier_medical, name="detail-dossier"
    ),

    path(
        "dossiers/download/<int:document_id>/",
        DownloadMedicalForm.as_view(),  
        name="download-dossier",
    ),

    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
