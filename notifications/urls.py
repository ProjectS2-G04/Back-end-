from django.urls import path
from .views import *

urlpatterns = [
    path('afficher_mes_notifications/', mes_notifications, name='mes_notifications'),
    path('marquer-toutes-lues/', marquer_toutes_notifications_lues, name='marquer_toutes_notifications_lues'),
    path('nouveau-count/', NombreNotificationsNonLuesView.as_view(), name='notifications-nouveau-count'),
    path('notifications/marquer-toutes-lues/', marquer_toutes_notifications_lues, name='marquer_toutes_notifications_lues'),
    path("marquer_comme_lu/<int:pk>/",MarkNotificationAsReadView.as_view(), name="notification" )
]
