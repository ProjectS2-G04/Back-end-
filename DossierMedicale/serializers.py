from rest_framework import serializers

from .models import *
from .models import validate_email, validate_phone_number







class DossierMedicaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = [ "id" , "nom" , "prenom"]



"""
class ArchiveDossierMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = ["id", "nom", "prenom"]

    def update(self, instance, validated_data):
        instance.is_archived = True  # Set is_archived to True
        instance.save()
        return instance"""







        
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

    def get_dossier_pdf_url(self, obj):
        request = self.context.get("request")  # Get request from context
        if obj.document_set.exists():
            document = obj.document_set.first()
            if document.file:
                return request.build_absolute_uri(document.file.url)
        return None


class DossierMedicalEtudiantSerializer(DossierMedicalSerializer):
    class Meta:
        model = DossierMedicalEtudiant
        fields = "__all__"


class DossierMedicalEnseignantSerializer(DossierMedicalSerializer):
    class Meta:
        model = DossierMedicalEnseignant
        fields = "__all__"


class DossierMedicalAtsSerializer(DossierMedicalSerializer):
    class Meta:
        model = DossierMedicalFonctionnaire
        fields = "__all__"


class DossierMedicalFonctionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedicalFonctionnaire
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
