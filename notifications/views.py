from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView 
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

class MarkNotificationAsReadView(APIView):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marquée comme lue."}, status=status.HTTP_200_OK)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_notification(request, id):
    try:
        notification = Notification.objects.get(id=id, user=request.user)
        notification.delete()
        return Response({"message": "Notification supprimée"}, status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response({"error": "Notification non trouvée"}, status=status.HTTP_404_NOT_FOUND)

    

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