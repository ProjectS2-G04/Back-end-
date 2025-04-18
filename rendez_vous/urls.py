from django.urls import include, path
from .views import *


urlpatterns = [
path ("create/<int:pk>/",OrdonnanceCreateView.as_view() ,  name='create-ordonnance'),
path ("list/",OrdonnanceListView.as_view() ,  name='list-des-ordonnances'),
path ("list/<int:id>/",OrdonnanceDetailView.as_view() ,  name='ordonnance'),
 path("my_ordonnances/", PatientOrdonnanceListView.as_view(), name="my_ordonnances"),
]