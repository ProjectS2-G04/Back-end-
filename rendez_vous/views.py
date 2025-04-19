from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import *
from .permissions import *
from datetime import date as dt_date
today_date = dt_date.today()
from .serializers import *
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

class OrdonnanceDetailView(RetrieveAPIView):
    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceDetailSerializer
    permission_classes = [IsAuthenticatedMedecin]
    lookup_field = 'id'


class PatientOrdonnanceListView(ListAPIView):
    serializer_class = OrdonnanceDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only ordonnances of the connected patient
        return Ordonnance.objects.filter(patient=self.request.user)
    

    
class OrdonnanceCreateView(APIView):
    permission_classes = [IsAuthenticatedMedecin]

    def post(self, request, pk ):
        
        age = request.data.get("age")
        try:
            patient = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "Patient not found."}, status=404)

        ordonnance = Ordonnance.objects.create(
            patient=patient,
            medecin=request.user,  # the authenticated doctor
            age=age,
            date=today_date
        )

        # Now create the medicaments
        medicaments_data = request.data.get("medicaments", [])
        for medicament in medicaments_data:
            Medicament.objects.create(
                nom=medicament["nom"],
                posologie=medicament["posologie"],
                duree=medicament["duree"],
                ordonnance=ordonnance
            )

        return Response({"message": "Ordonnance created successfully.", "ordonnance_id": ordonnance.id}, status=201)

class OrdonnanceListView(ListAPIView):
    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceSimpleSerializer
    permission_classes = [IsAuthenticatedMedecin]


from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from accounts.models import User
from rest_framework import generics, permissions, status
from datetime import datetime

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


class CreateDemandeRendezVousView(generics.CreateAPIView):
    queryset = DemandeRendezVous.objects.all()
    serializer_class = DemandeRendezVousSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.role != "PATIENT":
            return Response(
                {
                    "error": "Seuls les patients peuvent créer une demande de rendez-vous."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def confirmer_demande(request, demande_id):
    if not is_medecin_or_assistant(request.user):
        return Response(
            {
                "error": "Seuls les médecins ou assistants peuvent confirmer une demande."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Aucune demande avec cet ID n'existe."},
            status=status.HTTP_404_NOT_FOUND,
        )

    demande.statut = "confirmee"
    demande.save()
    return Response(
        {"success": "Demande confirmée avec succès."}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def annuler_demande(request, demande_id):
    if not is_medecin_or_assistant(request.user):
        return Response(
            {"error": "Seuls les médecins ou assistants peuvent annuler une demande."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND
        )

    demande.statut = "annulee"
    demande.save()
    return Response(
        {"success": "Demande annulée avec succès."}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reporter_demande(request, demande_id):
    if not is_medecin_or_assistant(request.user):
        return Response(
            {"error": "Seuls les médecins ou assistants peuvent reporter une demande."},
            status=status.HTTP_403_FORBIDDEN,
        )

    nouvelle_date = request.data.get("nouvelle_date")

    if not nouvelle_date:
        return Response(
            {"error": "La nouvelle date est requise."},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    try:
        datetime.strptime(nouvelle_date, "%Y-%m-%d")
    except ValueError:
        return Response(
            {"error": "Format de date invalide. Utilisez 'YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Demande non trouvée."}, status=status.HTTP_404_NOT_FOUND
        )

    demande.date_demandee = nouvelle_date
    demande.statut = "reportee"
    demande.save()
    return Response(
        {"success": f"Demande reportée à {nouvelle_date}."}, status=status.HTTP_200_OK
    )

def is_medecin_or_assistant(user):
    return user.role in ["DOCTOR", "ASSISTANT"]
