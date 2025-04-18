from rest_framework import serializers
from .models import DemandeRendezVous

class DemandeRendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeRendezVous
        fields = '__all__'
        read_only_fields = ['statut', 'patient', 'created_at']
