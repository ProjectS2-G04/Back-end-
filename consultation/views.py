from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Consultation, MaladieCronique, MaladieContagieuse
from rendez_vous.models import RendezVous
from django.utils import timezone

class AjouterConsultationView(APIView):
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

