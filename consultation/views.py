from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import ConsultationCreateSerializer
from .models import Consultation, MaladieCronique, MaladieContagieuse
from rendez_vous.models import RendezVous
from django.utils import timezone
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model


@api_view(["POST"])
def check_consultation_by_rendezvous(request, rendezvous_id):
    try:
        consultation = Consultation.objects.get(rendezvous__id=rendezvous_id)
        patient = consultation.rendezvous.patient

        return Response({
            "existe": True,
            "consultation_id": consultation.id,
            "patient_firstname": patient.first_name,
            "patient_lastname": patient.last_name
        }, status=status.HTTP_200_OK)

    except Consultation.DoesNotExist:
        return Response({
            "existe": False,
            "message": "Aucune consultation associée à ce rendez-vous."
        }, status=status.HTTP_200_OK)




class ConsultationDetailView(APIView):
    def get(self, request, consultation_id):
        try:
            consultation = Consultation.objects.select_related('rendezvous__patient').get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response({"error": "Consultation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        patient = consultation.rendezvous.patient

        # Check if an ordonnance is linked
        ordonnance_exists = hasattr(consultation, 'ordonnance') and consultation.ordonnance is not None

        data = {
            "nom": patient.last_name,
            "prenom": patient.first_name,
            "poids": consultation.poids,
            "taille": consultation.taille,
            "temperature": consultation.temperature,
            "date": consultation.date,
            "ordonnance_exist": ordonnance_exists,  # 👈 added field
        }

        return Response(data, status=status.HTTP_200_OK)










User = get_user_model()

class ConsultationsByPatientView(APIView):
    def get(self, request, patient_id):
        try:
            # Vérifier si le patient existe et a le bon rôle
            patient = User.objects.get(id=patient_id)
        except User.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

        email = patient.email

       
        rendezvous_list = RendezVous.objects.filter(patient=patient)

        # Chercher les consultations liées à ces rendez-vous
        consultations = Consultation.objects.filter(rendezvous__in=rendezvous_list)

        # Construire la réponse
        data = [
            {
                "consultation_id": consultation.id,
                "date": consultation.date.strftime("%Y-%m-%d"),
                "patient_email": email
            }
            for consultation in consultations
        ]

        return Response(data, status=status.HTTP_200_OK)


class AjouterConsultationView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            rendezvous = RendezVous.objects.get(id=pk)
        except RendezVous.DoesNotExist:
            return Response({"error": "Rendez-vous introuvable."}, status=404)

        # 💡 Check if a Consultation already exists
        if hasattr(rendezvous, 'consultation'):
            return Response({"error": "Une consultation existe déjà pour ce rendez-vous."}, status=400)

        serializer = ConsultationCreateSerializer(data=request.data, context={"rendezvous": rendezvous})

        if serializer.is_valid():
            consultation = serializer.save()
            return Response({"success": True, "consultation_id": consultation.id}, status=201)
        else:
            return Response(serializer.errors, status=400)










class AjouterConsultationViewTwo(APIView):
    #permission_classes = [IsAuthenticated]

    def post(self, request ,pk):
        data = request.data

        
        try:
            rendezvous = RendezVous.objects.get(id=pk)
        except RendezVous.DoesNotExist:
            return Response({"error": "Rendez-vous introuvable."}, status=404)

       
        consultation = Consultation.objects.create(
            rendezvous=rendezvous,
            poids=data.get("poids"),
            taille=data.get("taille"),
            tensionArterielle=data.get("tension"),
            date=data.get("date"),
            sexe=data.get("sexe"),
            temperature=data.get("temperature"),
            frequenceCardiaque=data.get("frequence"),
            test=data.get("test"),
            status=data.get("status"),
        )

        
        maladies_croniques = data.get("maladies_croniques", [])
        for maladie in maladies_croniques:
            MaladieCronique.objects.create(
                consultation=consultation,
                nom=maladie.get("nom"),
                sub_nom=maladie.get("sub_nom", "Diabète")
            )

        
        maladies_contagieuses = data.get("maladies_contagieuses", [])
        for nom in maladies_contagieuses:
            MaladieContagieuse.objects.create(consultation=consultation, nom=nom)

        return Response({"success": True, "consultation_id": consultation.id}, status=201)

