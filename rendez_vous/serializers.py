from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

class OrdonnanceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ordonnance
        fields = ['id', 'date']

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ['nom', 'posologie', 'duree']

class OrdonnanceSerializer(serializers.ModelSerializer):
    medicaments = MedicamentSerializer(many=True)

    class Meta:
        model = Ordonnance
        fields = ['age', 'date', 'medicaments']
    def create(self, validated_data):
        medicaments_data = validated_data.pop('medicaments')
        ordonnance = Ordonnance.objects.create(**validated_data)
        for medicament_data in medicaments_data:
            Medicament.objects.create(ordonnance=ordonnance, **medicament_data)
        return ordonnance    

class OrdonnanceDetailSerializer(serializers.ModelSerializer):
    patient_prenom = serializers.CharField(source='patient.first_name')
    patient_nom = serializers.CharField(source='patient.last_name')
    medicaments = MedicamentSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = ['id', 'age', 'date', 'patient_prenom', 'patient_nom', 'medicaments']         

    def create(self, validated_data):
        medicaments_data = validated_data.pop('medicaments')
        ordonnance = Ordonnance.objects.create(**validated_data)
        for medicament_data in medicaments_data:
            Medicament.objects.create(ordonnance=ordonnance, **medicament_data)
        return ordonnance







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

class RendezVousCreateSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    nom = serializers.CharField(source='patient.first_name', read_only=True)
    prenom = serializers.CharField(source='patient.last_name', read_only=True)
    class Meta:
        model = RendezVous
        fields = "__all__"
        read_only_fields = ['patient', 'medecin', 'assistant', 'created_at', 'statut']

class RendezVousMedAssCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = '__all__'
        read_only_fields = [
            'patient', 'medecin', 'assistant',
            'created_at', 'cree_par', 'modifie_par', 'statut'
        ]
class RendezVousPatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = '__all__'
        read_only_fields = [
            'patient',
            'medecin',
            'assistant',
            'cree_par',
            'modifie_par',
            'created_at',
            'statut'
        ]

class PlageHoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlageHoraire
        fields = ['id', 'date', 'heure_debut', 'heure_fin', 'statut', 'rendez_vous']