from django.urls import include, path
from .views import *

urlpatterns = [
    path('<int:pk>/', AjouterConsultationView.as_view(), name='ajouter-consultation'),
    path('patient/<int:patient_id>/', ConsultationsByPatientView.as_view(), name='consultations-by-patient'),
    path('detail/<int:consultation_id>/', ConsultationDetailView.as_view(), name='consultation-detail'),  
    path("check/<int:rendezvous_id>/", check_consultation_by_rendezvous , name = "check_consultation_by_rendezvous"),


]