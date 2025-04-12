from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import uuid
from accounts.models import User


def validate_phone_number(value):
    if not value.isdigit():
        raise ValidationError(
            "Le numéro de téléphone doit contenir uniquement des chiffres."
        )
    if len(value) != 10:
        raise ValidationError(
            "Le numéro de téléphone doit contenir exactement 10 chiffres."
        )


def validate_email(value):
    if not value.lower().endswith("esi-sba.dz"):
        raise ValidationError(
            "Seuls les emails se terminant par 'esi-sba.dz' sont autorisés."
        )


class DossierMedical(models.Model):
    GROUPE_SANGUIN_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]

    SEXE_CHOICES = [
        ("Homme", "Homme"),
        ("Femme", "Femme"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    photo = models.ImageField(
        upload_to="profile_pics", default="profile_pics/image.jpg"
    )

    is_archived = models.BooleanField(default=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=200)
    adresse = models.TextField()
    numero_telephone = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_phone_number],
        help_text="Entrez un numéro de téléphone de 10 chiffres.",
    )
    email = models.EmailField(
        unique=True,
        validators=[validate_email],
        help_text="Entrez l'email de l'école (doit se terminer par 'esi-sba.dz').",
    )
    service = models.CharField(max_length=100, null=True, blank=True)
    situation_familiale = models.CharField(max_length=100, null=True, blank=True)
    admission_etablissement = models.CharField(max_length=50, default="Oui")

    taille = models.FloatField(null=True, blank=True)
    poids = models.FloatField(null=True, blank=True)
    frequence_cardiaque = models.FloatField(null=True, blank=True)
    pression_arterielle = models.CharField(max_length=20, null=True, blank=True)

    numero_dossier = models.CharField(max_length=50, unique=True, blank=True)

    groupe_sanguin = models.CharField(
        max_length=3,
        choices=GROUPE_SANGUIN_CHOICES,
    )
    numero_securite_sociale = models.CharField(
        max_length=50, unique=True, null=True, blank=True
    )

    sexe = models.CharField(
        max_length=10,
        choices=SEXE_CHOICES,
        default="Homme",
    )

    fumeur = models.BooleanField(default=False)
    nombre_cigarettes = models.IntegerField(null=True, blank=True)
    chiqueur = models.BooleanField(default=False)
    nombre_boites_chique = models.IntegerField(null=True, blank=True)
    prise_autre = models.BooleanField(default=False)
    nombre_boites_autre = models.IntegerField(null=True, blank=True)
    age_premiere_prise = models.IntegerField(null=True, blank=True)
    ancien_fumeur = models.BooleanField(default=False)
    nombre_boites_fumeur = models.IntegerField(null=True, blank=True)

    affections_congenitales = models.TextField(null=True, blank=True)
    maladies_generales = models.TextField(null=True, blank=True)
    interventions_chirurgicales = models.TextField(null=True, blank=True)
    reactions_allergiques = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.numero_dossier:  # Only generate if not already set
            last_dossier = DossierMedical.objects.order_by("-id").first()
            last_num = 0  # Default to 0 if no valid dossier exists
            if (
                last_dossier
                and last_dossier.numero_dossier
                and last_dossier.numero_dossier.startswith("DOS")
            ):
                try:
                    last_num = int(last_dossier.numero_dossier[3:])
                except ValueError:
                    print(
                        f"Invalid numero_dossier format: {last_dossier.numero_dossier}"
                    )
                    last_num = 0
            self.numero_dossier = f"DOS{last_num + 1:03d}"  # e.g., DOS001

        # Nullify fields based on conditions
        if not self.fumeur:
            self.nombre_cigarettes = None
        if not self.chiqueur:
            self.nombre_boites_chique = None
        if not self.prise_autre:
            self.nombre_boites_autre = None
        if not self.ancien_fumeur:
            self.nombre_boites_fumeur = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dossier médical de {self.nom} {self.prenom}"


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    dossier_medical = models.ForeignKey(
        DossierMedical, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.title


class DossierMedicalEtudiant(DossierMedical):
    Filiere = models.CharField(max_length=30)
    Niveau = models.CharField(max_length=20)
    dossier_documents = models.ManyToManyField(
        Document, related_name="etudiants", blank=True
    )


class DossierMedicalEnseignant(DossierMedical):
    grade = models.CharField(max_length=20)
    specialite = models.CharField(max_length=100)
    dossier_documents = models.ManyToManyField(
        Document, related_name="enseignants", blank=True
    )


class DossierMedicalFonctionnaire(DossierMedical):
    grade = models.CharField(max_length=20)
    dossier_documents = models.ManyToManyField(
        Document, related_name="fonctionnaires", blank=True
    )
