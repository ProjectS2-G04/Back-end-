from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User


class RendezVous(models.Model):
    STATUT_CHOICES = [
        ("reserve", "Réservé"),
        ("termine", "Terminé"),
        ("annule", "Annulé"),
    ]

    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "PATIENT"},
        related_name="rendezvous_patient",
    )
    medecin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "DOCTOR"},
        related_name="rendezvous_medecin",
    )
    assistant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        limit_choices_to={"role": "ASSISTANT"},
        null=True,
        blank=True,
        related_name="rendezvous_assistant",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="reserve")

    def clean(self):
        if self.heure_fin <= self.heure_debut:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

    def __str__(self):
        return f"Rendez-vous le {self.date} ({self.heure_debut}-{self.heure_fin}) - Patient: {self.patient.email}"


class DemandeRendezVous(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("confirmee", "Confirmée"),
        ("reportee", "Reportée"),
        ("annulee", "Annulée"),
    ]

    TYPE_DEMANDE = [
        ("demande_rendez_vous", "Demande rendez-vous"),
        ("annulation_rendez_vous", "Annulation rendez-vous"),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "PATIENT"},
        related_name="demandes_rdv",
    )

    type = models.CharField(
        max_length=150, choices=TYPE_DEMANDE, default="demande_rendez_vous"
    )

    age = models.IntegerField()
    date_demandee = models.DateField()
    motif = models.CharField(max_length=255)
    description = models.TextField()
    statut = models.CharField(
        max_length=15, choices=STATUT_CHOICES, default="en_attente"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de rendez-vous pour le {self.date_demandee} - Patient: {self.patient.email}"


class PlageHoraire(models.Model):
    STATUT_CHOICES = [
        ("reserve", "Réservé"), # en rouge dans notre design
        ("termine", "Terminé"), # en vert
        ("grise", "Grisé"), # en gris
    ]

    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="reserve")
    rendez_vous = models.OneToOneField(
        RendezVous, on_delete=models.CASCADE, null=True, blank=True
    )

    def clean(self):
        if self.heure_fin <= self.heure_debut:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

    def __str__(self):
        return f"Plage horaire {self.date} ({self.heure_debut}-{self.heure_fin}) - Statut: {self.statut}"


class Ordonnance(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "PATIENT"},
        related_name="ordonnances_patient",
    )
    medecin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "DOCTOR"},
        related_name="ordonnances_medecin",
    )
    age = models.IntegerField() # we can replace this to make it auto calculated from dossier_medical
    date = models.DateField()

    def __str__(self):
        return f"Ordonnance du {self.date} - Patient: {self.patient.email} - Médecin: {self.medecin.email}"


class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    posologie = models.CharField(max_length=255)
    duree = models.CharField(max_length=50)
    ordonnance = models.ForeignKey(
        Ordonnance, on_delete=models.CASCADE, related_name="medicaments"
    )

    def __str__(self):
        return f"{self.nom} ({self.posologie} - {self.duree})"
