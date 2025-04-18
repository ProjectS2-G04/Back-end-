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





