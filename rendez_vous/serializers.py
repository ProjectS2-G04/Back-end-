from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
 

class RendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = "__all__"
        read_only_fields = ["patient", "medecin", "assistant", "created_at", "statut"]


class DemandeRendezVousSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    nom = serializers.CharField(source="patient.first_name", read_only=True)
    prenom = serializers.CharField(source="patient.last_name", read_only=True)

    class Meta:
        model = DemandeRendezVous
        fields = "__all__"
        read_only_fields = ["statut", "patient", "created_at"]
