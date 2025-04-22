from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.dateparse import parse_date, parse_time
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
            medecin=request.user, 
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


class CreateRendezVousView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, patient_id=None):
        if not patient_id:
            return Response(
                {"error": "L'ID du patient est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            patient = User.objects.get(id=patient_id, role="PATIENT")
        except User.DoesNotExist:
            return Response(
                {"error": "Le patient spécifié n'existe pas ou n'est pas valide."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = RendezVousCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if request.user.role in ["MEDECIN", "DOCTOR"]:
                    serializer.validated_data["medecin"] = request.user
                    assistant = User.objects.filter(
                        role__in=["ASSISTANT_MEDECIN", "ASSISTANT"]
                    ).first()
                    serializer.validated_data["assistant"] = assistant

                elif request.user.role in ["ASSISTANT_MEDECIN", "ASSISTANT"]:
                    serializer.validated_data["assistant"] = request.user
                    medecin = User.objects.filter(
                        role__in=["MEDECIN", "DOCTOR"]
                    ).first()
                    serializer.validated_data["medecin"] = medecin

                else:
                    return Response(
                        {"error": "Vous n'avez pas les permissions nécessaires."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                serializer.validated_data["patient"] = patient

                serializer.save()

                return Response(status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demandes_rendez_vous(request):
    demandes = DemandeRendezVous.objects.filter(type="demande_rendez_vous", statut="en_attente")
    serializer = DemandeRendezVousSerializer(demandes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demandes_annulation(request):
    demandes = DemandeRendezVous.objects.filter(type="annulation_rendez_vous")
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

class PlageHoraireListView(generics.ListAPIView):
    serializer_class = PlageHoraireSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        queryset = PlageHoraire.objects.all()

        if start and end:
            queryset = queryset.filter(date__range=[start, end])

        if user.role in ['MEDECIN', 'DOCTOR']:
            return queryset.filter(rendez_vous__medecin=user)

        elif user.role in ['ASSISTANT_MEDECIN', 'ASSISTANT']:
            return queryset.filter(rendez_vous__assistant=user)

        elif user.role == 'PATIENT':
            return queryset.filter(rendez_vous__patient=user)

        return PlageHoraire.objects.none()

class UpdatePlageHoraireStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        date = request.data.get("date")
        heure_debut = request.data.get("heure_debut")
        statut = request.data.get("statut")

        if not date or not heure_debut or not statut:
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plage = PlageHoraire.objects.get(date=parse_date(date), heure_debut=parse_time(heure_debut))
            plage.statut = statut
            plage.save()
            return Response({"message": "PlageHoraire updated successfully"})
        except PlageHoraire.DoesNotExist:
            return Response({"error": "PlageHoraire not found"}, status=status.HTTP_404_NOT_FOUND)

class SupprimerPlageEtAnnulerRDV(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        date = request.data.get("date")
        heure_debut = request.data.get("heure_debut")

        if not date or not heure_debut:
            return Response({"error": "Date et heure requises"}, status=400)

        try:
            plage = PlageHoraire.objects.get(date=date, heure_debut=heure_debut)

            # Annuler le rendez-vous lié s'il existe
            if plage.rendez_vous:
                plage.rendez_vous.statut = "annule"
                plage.rendez_vous.save()

            plage.delete()

            return Response({"message": "Plage supprimée et rendez-vous annulé"}, status=200)

        except PlageHoraire.DoesNotExist:
            return Response({"error": "Plage non trouvée"}, status=404)


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
