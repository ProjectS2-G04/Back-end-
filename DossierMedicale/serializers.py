from rest_framework import serializers
from .models import DossierMedical, DossierMedicalEtudiant, DossierMedicalEnseignant, DossierMedicalFonctionnaire, Document
from .models import validate_email, validate_phone_number

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

    def get_dossier_pdf_url(self, obj):
        request = self.context.get("request")  # Get request from context
        # obj is a DossierMedical instance; check its related documents via dossier_documents
        if hasattr(obj, 'dossier_documents') and obj.dossier_documents.exists():
            document = obj.dossier_documents.first()  # Get the first related document
            if document.file:
                return request.build_absolute_uri(document.file.url)
        return None

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class DossierMedicalEtudiantSerializer(DossierMedicalSerializer):
    dossier_documents = DocumentSerializer(many=True, read_only=True)  # Use DocumentSerializer

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