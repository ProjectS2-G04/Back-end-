from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion

def set_default_cree_par(apps, schema_editor):
    RendezVous = apps.get_model('rendez_vous', 'RendezVous')
    User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])
    default_user = User.objects.first()
    if default_user:
        for rdv in RendezVous.objects.filter(cree_par__isnull=True):
            rdv.cree_par = default_user
            rdv.save()

class Migration(migrations.Migration):

    dependencies = [
        ('rendez_vous', '0005_alter_rendezvous_cree_par_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(set_default_cree_par),
        migrations.AlterField(
            model_name='rendezvous',
            name='cree_par',
            field=models.ForeignKey(
                help_text='Utilisateur qui a créé le rendez-vous',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rdvs_crees',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

