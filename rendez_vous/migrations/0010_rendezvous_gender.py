# Generated by Django 5.2.1 on 2025-05-24 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rendez_vous', '0009_rendezvous_cree_par'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendezvous',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Homme'), ('Female', 'Femme')], max_length=10, null=True, verbose_name='Sexe'),
        ),
    ]
