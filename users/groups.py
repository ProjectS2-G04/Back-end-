from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from accounts.models import User 

def creer_permission(codename, nom):
    """Créer une nouvelle permission"""
    content_type = ContentType.objects.get_for_model(User)  
    permission, created = Permission.objects.get_or_create(
        codename=codename,
        name=nom,
        content_type=content_type,
    )
    if created:
        print(f"✅ Permission '{nom}' créée avec succès.")
    else:
        print(f"⚠️ La permission '{nom}' existe déjà.")
    return permission




def ajouter_permission_au_groupe(nom_groupe, codename_perm):
    """Ajouter une permission à un groupe"""
    try:
        groupe, created = Group.objects.get_or_create(name=nom_groupe)
        permission = Permission.objects.get(codename=codename_perm)
        groupe.permissions.add(permission)
        print(f"✅ Permission '{codename_perm}' ajoutée au groupe '{nom_groupe}'.")
    except Permission.DoesNotExist:
        print(f"⚠️ La permission '{codename_perm}' n'existe pas.")




def add_user_to_group(user_email, group_name):
    """Add a user to a group"""
    try:
        user = User.objects.get(email=user_email)
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        print(f"✅ L'utilisateur '{user_email}' a été ajouté au groupe '{group_name}'.")
    except User.DoesNotExist:
        print(f"⚠️ L'utilisateur avec l'email '{user_email}' n'existe pas.")
    except Group.DoesNotExist:
        print(f"⚠️ Le groupe '{group_name}' n'existe pas.")


def remove_user_from_group(user_email, group_name):
    """Remove a user from a group"""
    try:
        user = User.objects.get(email=user_email)
        group = Group.objects.get(name=group_name)

        if group in user.groups.all():
            user.groups.remove(group)
            print(f"✅ L'utilisateur '{user_email}' a été supprimé du groupe '{group_name}'.")
        else:
            print(f"⚠️ L'utilisateur '{user_email}' n'est pas dans le groupe '{group_name}'.")

    except User.DoesNotExist:
        print(f"⚠️ L'utilisateur avec l'email '{user_email}' n'existe pas.")
    except Group.DoesNotExist:
        print(f"⚠️ Le groupe '{group_name}' n'existe pas.")


#supprimer_utilisateur_du_groupe("admin@esi-sba.dz", "Admin")

