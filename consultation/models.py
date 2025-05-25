from django.db import models
from rendez_vous.models import *


class Consultation(models.Model):
    STATUS_CHOICES = [
        ("prise_en_charge", ("Prise en charge")),
        ("oriente", ("Orienté")),
    ]
    TEST_CHOICES = [
     ("Regulier" ,"Regulier "),
     ("Automatique" ,"Automatique"),
    ]
    rendezvous = models.OneToOneField(
        "rendez_vous.RendezVous", verbose_name=("consultation"), on_delete=models.CASCADE
    )
    poids = models.FloatField(verbose_name=("Poids"), null=True, blank=True)
    taille = models.FloatField(verbose_name=("Taille"), null=True, blank=True)
    tensionArterielle = models.FloatField(
        verbose_name=("Tension artérielle"), null=True, blank=True
    )
    temperature = models.FloatField(verbose_name=("Température"), null=True, blank=True)
    frequenceCardiaque = models.FloatField(
        verbose_name=("Fréquence cardiaque"), null=True, blank=True
    )
    test = models.CharField (max_length=30, choices=TEST_CHOICES , default ="Regulier")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="prise_en_charge",
        verbose_name=("Statut"),
    )

    def __str__(self):
        return f"Consultation - {self.rendezvous}"
    
class MaladieContagieuse(models.Model):

    consultation = models.ForeignKey(
        Consultation, verbose_name=("Consultation"), on_delete=models.CASCADE
    )
    nom = models.CharField(max_length=100, verbose_name=("Nom de la maladie"))
    def __str__(self):
        return self.nom

class MaladieCronique(models.Model):

    consultation = models.ForeignKey(
        Consultation, verbose_name=("Consultation"), on_delete=models.CASCADE
    )
    nom = models.CharField(max_length=100, verbose_name=("Nom de la maladie"))

    def __str__(self):
        return self.nom
    
    