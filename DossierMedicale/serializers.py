from rest_framework import serializers

from .models import (
    Document,
    DossierMedical,
    DossierMedicalEnseignant,
    DossierMedicalEtudiant,
    DossierMedicalFonctionnaire,
    validate_email,
    validate_phone_number,
)

from rest_framework import serializers
from .models import DossierMedicalFonctionnaire, Depistage, Document

class DepistageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depistage
        fields = [
            'evaluation_auditive',
            'utilisation_audiometre',
            'test_reponse_son',
            'remarque_audition',
            'vision_lointaine',
            'vision_proche',
            'besoin_lunettes',
            'test_snellen_effectue',
            'remarque_vision',
            'pression_oculaire',
            'examen_fond_oeil',
            'tests_ophtalmo_suppl',
            'maladies_oculaires_detectees',
            'examen_nez',
            'examen_oreille',
            'examen_larynx',
            'remarque_orl',
        ]





class DossierMedicaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = ["id", "nom", "prenom"]


class DossierMedicalSerializer(serializers.ModelSerializer):
    dossier_pdf_url = serializers.SerializerMethodField()

    def validate_numero_telephone(self, value):
        validate_phone_number(value)
        return value

    def validate_email(self, value):
        validate_email(value)
        return value

    class Meta:
        model = DossierMedical
        fields = "__all__"
        read_only_fields = ["imc", "categorie_imc"]

    def get_dossier_pdf_url(self, obj):
        request = self.context.get("request")
        if hasattr(obj, "dossier_documents") and obj.dossier_documents.exists():
            document = obj.dossier_documents.first()
            if document.file and hasattr(document.file, "url"):
                return (
                    request.build_absolute_uri(document.file.url) if request else None
                )
        return None


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class DossierMedicalEtudiantSerializer(DossierMedicalSerializer):
    dossier_documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DossierMedicalEtudiant
        fields = "__all__"
        read_only_fields = ["numero_dossier", "imc", "categorie_imc"]
        extra_kwargs = {
            "grade": {"write_only": True},  # Exclude from API response
            "specialite": {"write_only": True},
            "service": {"write_only": True},
        }

    def validate_Filiere(self, value):
        # Default to "Informatique" if empty
        return value or "Informatique"


class DossierMedicalEnseignantSerializer(DossierMedicalSerializer):
    dossier_documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DossierMedicalEnseignant
        fields = "__all__"
        read_only_fields = ["numero_dossier", "imc", "categorie_imc"]
        extra_kwargs = {
            "Filiere": {"write_only": True},
            "Niveau": {"write_only": True},
            "service": {"write_only": True},
        }


class DossierMedicalAtsSerializer(serializers.ModelSerializer):
    dossier_documents = DocumentSerializer(many=True, read_only=True)
    depistage = DepistageSerializer(read_only=True, allow_null=True)  # Allow null

    class Meta:
        model = DossierMedicalFonctionnaire
        fields = "__all__"
        read_only_fields = ["numero_dossier", "imc", "categorie_imc"]
        extra_kwargs = {
            "Filiere": {"write_only": True},
            "Niveau": {"write_only": True},
            "specialite": {"write_only": True},
        }
