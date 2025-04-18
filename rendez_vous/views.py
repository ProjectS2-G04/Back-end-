from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from accounts.models import User

#create rendezvous http://127.0.0.1:8000/api/rendez_vous/create/id /
class CreateRendezVousView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, patient_id=None):
        if not patient_id:
            return Response(
                {"error": "L'ID du patient est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            patient = User.objects.get(id=patient_id, role="PATIENT")
        except User.DoesNotExist:
            return Response(
                {"error": "Le patient spécifié n'existe pas ou n'est pas valide."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RendezVousSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Vérifier le rôle de l'utilisateur authentifié
                if request.user.role in ["MEDECIN", "DOCTOR"]:
                    serializer.validated_data['medecin'] = request.user
                    assistant = User.objects.filter(role__in=["ASSISTANT_MEDECIN", "ASSISTANT"]).first()
                    serializer.validated_data['assistant'] = assistant

                elif request.user.role in ["ASSISTANT_MEDECIN", "ASSISTANT"]:
                    serializer.validated_data['assistant'] = request.user
                    medecin = User.objects.filter(role__in=["MEDECIN", "DOCTOR"]).first()
                    serializer.validated_data['medecin'] = medecin

                else:
                    return Response(
                        {"error": "Vous n'avez pas les permissions nécessaires."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                    
                serializer.validated_data['patient'] = patient

                serializer.save()


                return Response(status=status.HTTP_201_CREATED)
                # return Response({"message": "Rendez-vous créé avec succès."}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Retourner les erreurs de validation si le serializer n'est pas valide
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# consulter la listes des demandes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demandes_rendez_vous(request):
    demandes = DemandeRendezVous.objects.filter(type='demande_rendez_vous')
    serializer = DemandeRendezVousSerializer(demandes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def demandes_annulation(request):
    demandes = DemandeRendezVous.objects.filter(type='annulation_rendez_vous')
    serializer = DemandeRendezVousSerializer(demandes, many=True)
    return Response(serializer.data)
