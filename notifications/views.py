from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView 
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def marquer_toutes_notifications_lues(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    count = notifications.update(is_read=True)
    return Response({"detail": f"{count} notifications marquées comme lues."}, status=status.HTTP_200_OK)

class NombreNotificationsNonLuesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"nombre_notifications_non_lues": count}, status=status.HTTP_200_OK)