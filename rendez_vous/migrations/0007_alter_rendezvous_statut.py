# Generated by Django 5.1.7 on 2025-05-01 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rendez_vous', '0006_alter_rendezvous_cree_par'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rendezvous',
            name='statut',
            field=models.CharField(choices=[('en-attente', 'En-attente'), ('reserve', 'Réservé'), ('repote', 'Reporte'), ('termine', 'Terminé'), ('annule', 'Annulé')], max_length=10),
        ),
    ]
