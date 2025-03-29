from rest_framework import serializers
from .models import *
from .models import validate_phone_number, validate_email


class DossierMedicalSerializer(serializers.ModelSerializer):

    def validate_numero_telephone(self, value):
        validate_phone_number(value)
        return value

    def validate_email(self, value):
        validate_email(value)
        return value

    class Meta:
        model = DossierMedical
        fields = "__all__"


class DossierMedicalEtudiantSerializer(DossierMedicalSerializer):
    class Meta:
        model = DossierMedicalEtudian
        fields = "__all__"


class DossierMedicalEnseignantSerializer(DossierMedicalSerializer):
    class Meta:
        model = DossierMedicalEnseignant
        fields = "__all__"


class DossierMedicalAtsSerializer(DossierMedicalSerializer):
    class Meta:
        model = DossierMedicalFonctionnaire
        fields = "__all__"


class DossierMedicalEtudianSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedicalEtudian
        fields = '__all__'

class DossierMedicalEnseignantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedicalEnseignant
        fields = '__all__'

class DossierMedicalFonctionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedicalFonctionnaire
        fields = '__all__'