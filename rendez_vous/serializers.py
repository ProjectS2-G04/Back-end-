from rest_framework import serializers
from .models import *

class OrdonnanceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ordonnance
        fields = ['id', 'date']


class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['nom', 'posologie', 'duree']

class OrdonnanceDetailSerializer(serializers.ModelSerializer):
    patient_prenom = serializers.CharField(source='patient.first_name')
    patient_nom = serializers.CharField(source='patient.last_name')
    medicaments = MedicamentSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = ['id', 'age', 'date', 'patient_prenom', 'patient_nom', 'medicaments']





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
        fields = '__all__'
        read_only_fields = ['statut', 'patient', 'created_at']
        fields = "__all__"
        read_only_fields = ["statut", "patient", "created_at"]
