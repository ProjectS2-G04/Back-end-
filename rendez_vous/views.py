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

class OrdonnanceDetailByConsultationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response({"error": "Consultation introuvable"}, status=status.HTTP_404_NOT_FOUND)

        try:
            ordonnance = Ordonnance.objects.get(consultation=consultation)
        except Ordonnance.DoesNotExist:
            return Response({"message": "Aucune ordonnance n'est associée à cette consultation."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrdonnanceDetailSerializer(ordonnance)
        return Response(serializer.data, status=status.HTTP_200_OK)






class OrdonnanceDetailView(RetrieveAPIView):
    queryset = Ordonnance.objects.all()
    serializer_class = OrdonnanceDetailSerializer
    #permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class PatientOrdonnanceListView(ListAPIView):
    serializer_class = OrdonnanceDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ordonnance.objects.filter(patient=self.request.user)
    
class OrdonnanceCreateView(APIView):
    permission_classes = [IsAuthenticatedMedecin]

    def post(self, request, pk):
        try:
            consultation = Consultation.objects.get(id=pk)
        except Consultation.DoesNotExist:
            return Response({"error": "Consultation not found."}, status=404)
        
        if Ordonnance.objects.filter(consultation=consultation).exists():
            return Response({"message": "Cette consultation a déjà une ordonnance."}, status=400) 
        patient = consultation.rendezvous.patient
        medecin = request.user
        
        data = request.data.copy()
      

        serializer = OrdonnanceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(
                patient=patient,
                medecin=medecin,
                consultation=consultation
            )
            return Response({
                "message": "Ordonnance created successfully.",
                "ordonnance_id": serializer.instance.id
            }, status=201)

        return Response(serializer.errors, status=400)

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

            if plage.rendez_vous:
                plage.rendez_vous.statut = "annule"
                plage.rendez_vous.save()

            plage.delete()

            return Response({"message": "Plage supprimée et rendez-vous annulé"}, status=200)

        except PlageHoraire.DoesNotExist:
            return Response({"error": "Plage non trouvée"}, status=404)

class CreatePlageHoraireView(generics.CreateAPIView):
    queryset = PlageHoraire.objects.all()
    serializer_class = PlageHoraireSerializer
    permission_classes = [IsAuthenticated]


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
def annuler_demande_patient(request, demande_id):
    if not is_patient(request.user):
        return Response(
            {"error": "Seuls les patinets peuvent envoyer demande d'annulation du rdv."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        demande = DemandeRendezVous.objects.get(id=demande_id)
    except DemandeRendezVous.DoesNotExist:
        return Response(
            {"error": "Demande introuvable."}, status=status.HTTP_404_NOT_FOUND
        )

    demande.type = "annulation_rendez_vous"
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

def is_patient(user):
    return user.role in ["PATIENT"]

class CreateRendezVousParMedAssView(APIView):
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

        serializer = RendezVousMedAssCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = request.user
                validated_data = serializer.validated_data

                # Déterminer qui est médecin / assistant
                if user.role in ["MEDECIN", "DOCTOR"]:
                    validated_data["medecin"] = user
                    validated_data["assistant"] = User.objects.filter(
                        role__in=["ASSISTANT", "ASSISTANT_MEDECIN"]
                    ).first()
                elif user.role in ["ASSISTANT", "ASSISTANT_MEDECIN"]:
                    validated_data["assistant"] = user
                    validated_data["medecin"] = User.objects.filter(
                        role__in=["MEDECIN", "DOCTOR"]
                    ).first()
                else:
                    return Response(
                        {"error": "Vous n'avez pas les permissions nécessaires."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                validated_data["patient"] = patient
                validated_data["cree_par"] = user
                validated_data["statut"] = "reserve"  # Fixé automatiquement

                rendez_vous = RendezVous.objects.create(**validated_data)

                return Response(
                    RendezVousCreateSerializer(rendez_vous).data,
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CreateRendezVousParPatientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RendezVousPatientCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                medecin = User.objects.filter(role__in=["MEDECIN", "DOCTOR"]).first()
                assistant = User.objects.filter(role__in=["ASSISTANT_MEDECIN", "ASSISTANT"]).first()

                serializer.validated_data["patient"] = request.user
                serializer.validated_data["cree_par"] = request.user
                serializer.validated_data["statut"] = "en-attente"
                serializer.validated_data["medecin"] = medecin
                serializer.validated_data["assistant"] = assistant

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
