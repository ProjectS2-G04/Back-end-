# Generated by Django 5.1.7 on 2025-05-01 18:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rendez_vous', '0005_alter_rendezvous_cree_par_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='rendezvous',
            name='cree_par',
            field=models.ForeignKey(help_text='Utilisateur qui a créé le rendez-vous', on_delete=django.db.models.deletion.CASCADE, related_name='rdvs_crees', to=settings.AUTH_USER_MODEL),
        ),
    ]
