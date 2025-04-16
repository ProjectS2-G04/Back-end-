from django.db import models
from django.conf import settings


class NotificationType(models.TextChoices):
    DEMANDE_RDV_RECUE = "DEMANDE_RDV_RECUE", "Demande de rendez-vous reçue"
    RDV_CONFIRMEE = "RDV_CONFIRMEE", "Rendez-vous confirmé"
    RDV_ANNULE = "RDV_ANNULE", "Rendez-vous annulé"
    RDV_RAPPORTE = "RDV_RAPPORTE", "Rendez-vous raporté a une autre date"
    RDV_PLANNIFIE = "RDV_PLANNIFIE", "Nouveau rendez-vous plannifié"
    RDV_TERMINE = "RDV_TERMINE", "Rendez-vous terminé"
    RDV_EN_ATTENTE = "RDV_EN_ATTENTE", "Rendez-vous en attente"
    RAPPEL_RDV = "RAPPEL_RDV", "Rappel de rendez-vous"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Utilisateur qui reçoit la notification"
    )

    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.DEMANDE_RDV_RECUE,
        help_text="Type de notification"
    )

    message = models.TextField(help_text="Contenu de la notification")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    lien_action = models.URLField(
        blank=True,
        null=True,
        help_text="Lien vers l'action ou la ressource associée"
    )

    rendez_vous = models.ForeignKey(
        "rendez_vous.RendezVous",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications",
        help_text="Rendez-vous concerné par la notification"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.user}] {self.get_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
