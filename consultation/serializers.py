from rest_framework import serializers
from .models import Consultation, MaladieCronique, MaladieContagieuse
from rendez_vous.models import RendezVous

class MaladieCroniqueSerializer(serializers.Serializer):
    nom = serializers.CharField()
    sub_nom = serializers.CharField(default="Diabète")

class ConsultationCreateSerializer(serializers.Serializer):
    poids = serializers.FloatField(allow_null=True, required=False)
    taille = serializers.FloatField(allow_null=True, required=False)
    tension = serializers.FloatField(allow_null=True, required=False)
    date = serializers.DateField()
    sexe = serializers.ChoiceField(choices=Consultation.SEXE_CHOICES)
    temperature = serializers.FloatField(allow_null=True, required=False)
    frequence = serializers.FloatField(allow_null=True, required=False)
    test = serializers.ChoiceField(choices=Consultation.TEST_CHOICES)
    status = serializers.ChoiceField(choices=Consultation.STATUS_CHOICES)

    maladies_croniques = MaladieCroniqueSerializer(many=True, required=False)
    maladies_contagieuses = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    def create(self, validated_data):
        rendezvous = self.context.get('rendezvous')
        maladies_croniques_data = validated_data.pop("maladies_croniques", [])
        maladies_contagieuses_data = validated_data.pop("maladies_contagieuses", [])

        consultation = Consultation.objects.create(
            rendezvous=rendezvous,
            poids=validated_data.get("poids"),
            taille=validated_data.get("taille"),
            tensionArterielle=validated_data.get("tension"),
            date=validated_data.get("date"),
            sexe=validated_data.get("sexe"),
            temperature=validated_data.get("temperature"),
            frequenceCardiaque=validated_data.get("frequence"),
            test=validated_data.get("test"),
            status=validated_data.get("status"),
        )

        for maladie in maladies_croniques_data:
            MaladieCronique.objects.create(
                consultation=consultation,
                nom=maladie["nom"],
                sub_nom=maladie.get("sub_nom")
            )

        for nom in maladies_contagieuses_data:
            MaladieContagieuse.objects.create(
                consultation=consultation,
                nom=nom
            )

        return consultation
