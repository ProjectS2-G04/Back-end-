from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rendez_vous.models import RendezVous
from .models import Notification
from users.models import User


@receiver(pre_save, sender=RendezVous)
def set_old_statut(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = RendezVous.objects.get(pk=instance.pk)
            instance._old_statut = old_instance.statut
        except RendezVous.DoesNotExist:
            instance._old_statut = None
    else:
        instance._old_statut = None

@receiver(post_save, sender=RendezVous)
def new_rdv_notification(sender, instance, created, **kwargs):
    if not created:
        return  

    rdv_date = instance.Datetime.strftime('%d/%m/%Y %H:%M')
    patient = instance.patient
    statut = instance.statut

    if statut == "en-attente":
        for user in User.objects.filter(role__in=["DOCTOR", "ASSISTANT"]):
            Notification.objects.create(
                user=user,
                message=f"{patient.first_name} {patient.last_name} a demandé un rendez-vous le {rdv_date}.",
                is_read=False,
                rendez_vous=instance
            )

    elif statut == "reserve":
        # Notification pour le patient
        Notification.objects.create(
            user=patient,
            message=f"Un rendez-vous a été planifié pour vous le {rdv_date}.",
            is_read=False,
            rendez_vous=instance
        )

        # Notification pour les médecins si créé par assistant
        if instance.cree_par and instance.cree_par.role in ["ASSISTANT", "ASSISTANT_MEDECIN"]:
            for medecin in User.objects.filter(role__in=["DOCTOR", "MEDECIN"]):
                Notification.objects.create(
                    user=medecin,
                    message=f"Un rendez-vous a été planifié pour {patient.first_name} {patient.last_name}  le {rdv_date}.",
                    is_read=False,
                    rendez_vous=instance
                )

        # Notification pour les assistants si créé par médecin
        elif instance.cree_par and instance.cree_par.role in ["DOCTOR", "MEDECIN"]:
            for assistant in User.objects.filter(role__in=["ASSISTANT", "ASSISTANT_MEDECIN"]):
                Notification.objects.create(
                    user=assistant,
                    message=f"Un rendez-vous a été planifié pour {patient.first_name} {patient.last_name} le {rdv_date}.",
                    is_read=False,
                    rendez_vous=instance
                )
        
@receiver(post_save, sender=RendezVous)
def update_rdv_notification(sender, instance, created, **kwargs):
    if created:
        return 

    old_statut = getattr(instance, '_old_statut', None)
    new_statut = instance.statut
    patient = instance.patient
    modificateur = instance.modifie_par
    role = modificateur.role if modificateur else None
    rdv_date = instance.Datetime.strftime('%d/%m/%Y %H:%M')

    def notify_roles(roles, message):
        for user in User.objects.filter(role__in=roles).exclude(id=modificateur.id if modificateur else None):
            Notification.objects.create(
                user=user,
                message=message,
                is_read=False,
                rendez_vous=instance
            )

    # Confirmation
    if old_statut == "en-attente" and new_statut == "reserve":
        Notification.objects.create(
            user=patient,
            message=f"Votre demande de rendez-vous a été confirmée pour le {rdv_date}.",
            is_read=False,
            rendez_vous=instance
        )
        if role == "DOCTOR":
            notify_roles(["ASSISTANT"], f"Le médecin a confirmé le rendez-vous de {patient.first_name} {patient.last_name} pour le {rdv_date}.")
        elif role == "ASSISTANT":
            notify_roles(["DOCTOR"], f"L'assistant a confirmé le rendez-vous de {patient.first_name} {patient.last_name} pour le {rdv_date}.")

    # Report d'un demande rendez vous
    elif old_statut == "en-attente" and new_statut == "repote":
        Notification.objects.create(
            user=patient,
            message=f"Votre demande de rendez-vous a été reporté au {rdv_date}.",
            is_read=False,
            rendez_vous=instance
        )
        if role == "DOCTOR":
            notify_roles(["ASSISTANT"], f"Le médecin a reporté le demande de rendez-vous de {patient.first_name} {patient.last_name} au {rdv_date}.")
        elif role == "ASSISTANT":
            notify_roles(["DOCTOR"], f"L'assistant a reporté le demande de rendez-vous de {patient.first_name} {patient.last_name} au {rdv_date}.")
    elif old_statut != "en-attente" and new_statut == "repote":
        Notification.objects.create(
            user=patient,
            message=f"Votre  rendez-vous a été reporté au {rdv_date}.",
            is_read=False,
            rendez_vous=instance
        )
        if role == "DOCTOR":
            notify_roles(["ASSISTANT"], f"Le médecin a reporté le rendez-vous de {patient.first_name} {patient.last_name} au {rdv_date}.")
        elif role == "ASSISTANT":
            notify_roles(["DOCTOR"], f"L'assistant a reporté le rendez-vous de {patient.first_name} {patient.last_name} au {rdv_date}.")

    # Annulation par médecin/assistant
    elif new_statut == "annule" and role in ["DOCTOR", "ASSISTANT"]:
        Notification.objects.create(
            user=patient,
            message=f"Votre rendez-vous du {rdv_date} a été annulé.",
            is_read=False,
            rendez_vous=instance
        )
        if role == "DOCTOR":
            notify_roles(["ASSISTANT"], f"Le médecin a annulé le rendez-vous de {patient.first_name} {patient.last_name} prévu le {rdv_date}.")
        elif role == "ASSISTANT":
            notify_roles(["DOCTOR"], f"L'assistant a annulé le rendez-vous de {patient.first_name} {patient.last_name} prévu le {rdv_date}.")

    # Annulation par patient
    elif new_statut == "annule" and role == "PATIENT":
        if old_statut == "en-attente":
            notifications = Notification.objects.filter(
                rendez_vous=instance,
                user__role__in=["DOCTOR", "ASSISTANT"]
            )
            if notifications.exists() and all(notif.is_read is False for notif in notifications):
                notifications.delete()
            else:
                for user in User.objects.filter(role__in=["DOCTOR", "ASSISTANT"]):
                    Notification.objects.create(
                        user=user,
                        message=f"{patient.first_name} {patient.last_name} a annulé sa demande de rendez-vous du {rdv_date}.",
                        is_read=False,
                        rendez_vous=instance
                    )
        else:
            for user in User.objects.filter(role__in=["DOCTOR", "ASSISTANT"]):
                Notification.objects.create(
                    user=user,
                    message=f"{patient.first_name} {patient.last_name} a annulé le rendez-vous du {rdv_date}.",
                    is_read=False,
                    rendez_vous=instance
                )
    # Terminé
    elif new_statut == "termine":
        Notification.objects.create(
            user=patient,
            message=f"Votre rendez-vous du {rdv_date} est terminé. Merci pour votre visite.",
            is_read=False,
            rendez_vous=instance
        )
