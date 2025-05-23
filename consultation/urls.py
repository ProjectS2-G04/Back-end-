from django.urls import include, path
from .views import *

urlpatterns = [
    path('<int:pk>/', AjouterConsultationView.as_view(), name='ajouter-consultation'),
]