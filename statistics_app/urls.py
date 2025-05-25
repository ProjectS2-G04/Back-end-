from django.urls import path
from .views import DashboardStatsView, ChronicDiseasesStatsView, ContagiousDiseasesStatsView

urlpatterns = [
    path('api/dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('api/chronic-diseases-stats/', ChronicDiseasesStatsView.as_view(), name='chronic-diseases-stats'),
    path('api/contagious-diseases-stats/', ContagiousDiseasesStatsView.as_view(), name='contagious-diseases-stats'),
]