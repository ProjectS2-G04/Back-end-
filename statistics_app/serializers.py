from rest_framework import serializers
from consultation.models import Consultation, MaladieContagieuse, MaladieCronique

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['id', 'rendezvous', 'poids', 'taille', 'tensionArterielle', 'temperature', 'frequenceCardiaque', 'test', 'status']

class MaladieContagieuseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaladieContagieuse
        fields = ['id', 'consultation', 'nom']

class MaladieCroniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaladieCronique
        fields = ['id', 'consultation', 'nom']

class ChronicDiseaseStatsSerializer(serializers.Serializer):
    name = serializers.CharField()
    Homme = serializers.IntegerField()
    Femme = serializers.IntegerField()

class ContagiousDiseaseBarSerializer(serializers.Serializer):
    name = serializers.CharField()
    Homme = serializers.IntegerField()
    Femme = serializers.IntegerField()

class ContagiousDiseasePieSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()