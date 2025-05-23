from django.urls import include, path
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("create/<int:pk>/", OrdonnanceCreateView.as_view(), name="create-ordonnance"),
    path("list/", OrdonnanceListView.as_view(), name="list-des-ordonnances"),
    path("list/<int:id>/", OrdonnanceDetailView.as_view(), name="ordonnance"),
    path("my_ordonnances/", PatientOrdonnanceListView.as_view(), name="my_ordonnances"),
    path(
        "createrenderVousMedAss/<int:patient_id>/",
        CreateRendezVousParMedAssView.as_view(),
        name="create-rendezvous_MedAss",
    ),
    path(
        "createrenderVousPatient/",
        CreateRendezVousParPatientView.as_view(),
        name="create-rendezvous_patient",
    ),
    path("demandes/rdv/", demandes_rendez_vous, name="demandes_rdv"),
    path("demandes/annulation/", demandes_annulation, name="demandes_annulation"),
    path(
        "demande/create/",
        views.CreateDemandeRendezVousView.as_view(),
        name="create-demande",
    ),
    path(
        "demande/<int:demande_id>/confirmer/",
        views.confirmer_demande,
        name="confirmer-demande",
    ),
    path(
        "demande/<int:demande_id>/annuler/",
        views.annuler_demande,
        name="annuler-demande",
    ),
    path(
        "demande/<int:demande_id>/reporter/",
        views.reporter_demande,
        name="reporter-demande",
    ),
    path(
        "create/<int:patient_id>/",
        CreateRendezVousView.as_view(),
        name="create-rendezvous",
    ),
    path("demandes/rdv/", demandes_rendez_vous, name="demandes_rdv"),
    path("demandes/annulation/", demandes_annulation, name="demandes_annulation"),
    path(
        "demande/create/",
        views.CreateDemandeRendezVousView.as_view(),
        name="create-demande",
    ),
    path(
        "demande/<int:demande_id>/confirmer/",
        views.confirmer_demande,
        name="confirmer-demande",
    ),
    path(
        "demande/<int:demande_id>/annuler/",
        views.annuler_demande,
        name="annuler-demande",
    ),
    path(
        "demande/<int:demande_id>/annuler-demande-patient/",
        views.annuler_demande_patient,
        name="annuler-demande-patient",
    ),
    path(
        "demande/<int:demande_id>/reporter/",
        views.reporter_demande,
        name="reporter-demande",
    ),
    path("plages_horaires/", PlageHoraireListView.as_view(), name="plages-horaires"),
    path("plages_horaires/update/", UpdatePlageHoraireStatusView.as_view(), name="update-plage-horaire"),
    path("plages_horaires/delete_and_cancel/", SupprimerPlageEtAnnulerRDV.as_view(), name="delete-plage-and-cancel-rdv"),
    path("plages_horaires/create/", CreatePlageHoraireView.as_view(), name="plage-horaire-create"),

]
