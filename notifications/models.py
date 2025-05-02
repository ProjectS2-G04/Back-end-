from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Utilisateur qui reçoit la notification"
    )
    
    message = models.TextField(help_text="Contenu de la notification")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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
        return f"[{self.user}] {self.message} "