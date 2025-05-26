from datetime import datetime
import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from .models import *
from django.utils import timezone
logger = logging.getLogger(__name__)

class OrdonnanceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ordonnance
        fields = ["id", "date"]

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = ["nom", "posologie", "duree"]

class OrdonnanceSerializer(serializers.ModelSerializer):
    medicaments = MedicamentSerializer(many=True)

    class Meta:
        model = Ordonnance
        fields = ["age", "date", "medicaments"]

    def create(self, validated_data):
        medicaments_data = validated_data.pop("medicaments")
        ordonnance = Ordonnance.objects.create(**validated_data)
        for medicament_data in medicaments_data:
            Medicament.objects.create(ordonnance=ordonnance, **medicament_data)
        return ordonnance

class OrdonnanceDetailSerializer(serializers.ModelSerializer):
    patient_prenom = serializers.CharField(source="patient.first_name")
    patient_nom = serializers.CharField(source="patient.last_name")
    medicaments = MedicamentSerializer(many=True, read_only=True)

    class Meta:
        model = Ordonnance
        fields = ["id", "age", "date", "patient_prenom", "patient_nom", "medicaments"]

    def create(self, validated_data):
        medicaments_data = validated_data.pop("medicaments")
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
        fields = "__all__"
        read_only_fields = ["statut", "patient", "created_at"]

class RendezVousCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source="motif", required=True)
    date = serializers.DateField(write_only=True, required=True)
    heure_debut = serializers.TimeField(write_only=True, required=True)
    heure_fin = serializers.TimeField(write_only=True, required=True)
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    nom = serializers.CharField(source="patient.first_name", read_only=True)
    prenom = serializers.CharField(source="patient.last_name", read_only=True)

    class Meta:
        model = RendezVous
        fields = [
            "description",
            "date",
            "heure_debut",
            "heure_fin",
            "patient",
            "patient_id",
            "nom",
            "prenom",
            "medecin",
            "assistant",
            "statut",
            "cree_par",
            "created_at",
            "Datetime",
            "duree",
        ]
        read_only_fields = [
            "patient",
            "medecin",
            "assistant",
            "statut",
            "cree_par",
            "created_at",
            "patient_id",
            "nom",
            "prenom",
        ]

    def validate(self, data):
        date = data.get("date")
        heure_debut = data.get("heure_debut")
        heure_fin = data.get("heure_fin")

        if date and heure_debut:
            try:
                data["Datetime"] = datetime.combine(
                    date, heure_debut, tzinfo=timezone.get_current_timezone()
                )
            except ValueError:
                raise serializers.ValidationError(
                    {"Datetime": "Invalid date or time format."}
                )

        if heure_debut and heure_fin:
            if heure_fin <= heure_debut:
                raise serializers.ValidationError(
                    {"heure_fin": "L'heure de fin doit être après l'heure de début."}
                )
            duration = (
                datetime.combine(date, heure_fin) - datetime.combine(date, heure_debut)
            ).seconds
            hours, remainder = divmod(duration, 3600)
            minutes, _ = divmod(remainder, 60)
            data["duree"] = f"{hours:02d}:{minutes:02d}:00"

        return data

    def create(self, validated_data):
        validated_data.pop("date", None)
        validated_data.pop("heure_debut", None)
        validated_data.pop("heure_fin", None)
        return super().create(validated_data)

class RendezVousMedAssCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='motif', required=True)
    date = serializers.DateField(write_only=True, required=True)
    heure_debut = serializers.TimeField(write_only=True, required=True, format='%H:%M')
    heure_fin = serializers.TimeField(write_only=True, required=True, format='%H:%M')
    duree = serializers.CharField(read_only=True)

    class Meta:
        model = RendezVous
        fields = [
            'description', 'date', 'heure_debut', 'heure_fin', 'duree',
            'patient', 'medecin', 'assistant', 'statut',
            'cree_par', 'modifie_par', 'created_at'
        ]
        read_only_fields = [
            'patient', 'medecin', 'assistant', 'statut',
            'cree_par', 'modifie_par', 'created_at', 'duree'
        ]

    def validate(self, data):
        logger.info(f"Serializer input data: {data}")
        date = data.get('date')
        heure_debut = data.get('heure_debut')
        heure_fin = data.get('heure_fin')

        if not all([date, heure_debut, heure_fin]):
            logger.error(f"Missing fields: date={date}, heure_debut={heure_debut}, heure_fin={heure_fin}")
            raise serializers.ValidationError({
                "error": "All fields (date, heure_debut, heure_fin) are required."
            })

        if heure_fin <= heure_debut:
            logger.error("heure_fin is not after heure_debut")
            raise serializers.ValidationError({
                "heure_fin": "L'heure de fin doit être après l'heure de début."
            })

        try:
            data['Datetime'] = datetime.combine(
                date, heure_debut, tzinfo=timezone.get_current_timezone()
            )
            logger.info(f"Set Datetime: {data['Datetime']}")
        except (ValueError, TypeError) as e:
            logger.error(f"Datetime validation error: {str(e)}")
            raise serializers.ValidationError({"Datetime": f"Invalid date or time format: {str(e)}"})

        duration = (datetime.combine(date, heure_fin) - datetime.combine(date, heure_debut)).seconds
        hours, remainder = divmod(duration, 3600)
        minutes, _ = divmod(remainder, 60)
        data['duree'] = f"{hours:02d}:{minutes:02d}:00"

        logger.info(f"Validated data: {data}")
        return data

    def create(self, validated_data):
        logger.info(f"Creating with validated_data: {validated_data}")
        validated_data.pop('date', None)
        validated_data.pop('heure_debut', None)
        validated_data.pop('heure_fin', None)
        validated_data.pop('duree', None)
        return super().create(validated_data)

class RendezVousPatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = "__all__"
        read_only_fields = [
            "patient",
            "medecin",
            "assistant",
            "cree_par",
            "modifie_par",
            "created_at",
            "statut",
        ]

class PlageHoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlageHoraire
        fields = ["id", "date", "heure_debut", "heure_fin", "statut", "rendez_vous"]