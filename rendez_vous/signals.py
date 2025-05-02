from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import RendezVous, PlageHoraire
from datetime import datetime, time, timedelta


# @receiver(post_save, sender=RendezVous)
# def create_plage_horaire_for_rendezvous(sender, instance, created, **kwargs):
#     if created:
#         heure_debut_ronde = time(hour=instance.heure_debut.hour)

#         fin_hour = instance.heure_fin.hour + (
#             1 if instance.heure_fin.minute > 0 or instance.heure_fin.second > 0 else 0
#         )
#         heure_fin_ronde = time(hour=fin_hour if fin_hour < 24 else 23, minute=0)

#         debut_dt = datetime.combine(instance.date, instance.heure_debut)
#         fin_dt = datetime.combine(instance.date, instance.heure_fin)
#         duration = fin_dt - debut_dt

#         if duration > timedelta(hours=1):
#             print(f"⚠️ Durée du rendez-vous supérieure à 1 heure: {duration}")

#         PlageHoraire.objects.create(
#             date=instance.date,
#             heure_debut=heure_debut_ronde,
#             heure_fin=heure_fin_ronde,
#             statut="reserve",
#             rendez_vous=instance,
#         )


# @receiver(pre_save, sender=RendezVous)
# def delete_plage_horaire_if_annulee(sender, instance, **kwargs):
#     if instance.pk:
#         previous = RendezVous.objects.get(pk=instance.pk)
#         if previous.statut != "annule" and instance.statut == "annule":
#             try:
#                 plage = PlageHoraire.objects.get(rendez_vous=instance)
#                 plage.delete()
#             except PlageHoraire.DoesNotExist:
#                 pass
