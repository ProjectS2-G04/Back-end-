from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User  

class Command(BaseCommand):
    help = "Créer les groupes et assigner les permissions"

    def handle(self, *args, **kwargs):
        roles = {
            "Admin": [],
            "Médecin": [],
            "Assistant Médecin": [],
            "Directeur": [],
            "Patient": [],
        }

        for role, permissions in roles.items():
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Groupe '{role}' créé."))

            for perm_codename in permissions:
                try:
                    perm = Permission.objects.get(codename=perm_codename)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Permission '{perm_codename}' introuvable."))

            self.stdout.write(self.style.SUCCESS(f"Permissions attribuées au groupe '{role}'."))