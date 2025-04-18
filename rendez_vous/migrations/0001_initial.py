# Generated by Django 5.1.7 on 2025-04-16 21:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DemandeRendezVous',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('demande_rendez_vous', 'Demande rendez-vous'), ('annulation_rendez_vous', 'Annulation rendez-vous')], default='demande_rendez_vous', max_length=150)),
                ('age', models.IntegerField()),
                ('date_demandee', models.DateField()),
                ('motif', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('confirmee', 'Confirmée'), ('reportee', 'Reportée'), ('annulee', 'Annulée')], default='en_attente', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(limit_choices_to={'role': 'PATIENT'}, on_delete=django.db.models.deletion.CASCADE, related_name='demandes_rdv', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ordonnance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('date', models.DateField()),
                ('medecin', models.ForeignKey(limit_choices_to={'role': 'DOCTOR'}, on_delete=django.db.models.deletion.CASCADE, related_name='ordonnances_medecin', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(limit_choices_to={'role': 'PATIENT'}, on_delete=django.db.models.deletion.CASCADE, related_name='ordonnances_patient', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Medicament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('posologie', models.CharField(max_length=255)),
                ('duree', models.CharField(max_length=50)),
                ('ordonnance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicaments', to='rendez_vous.ordonnance')),
            ],
        ),
        migrations.CreateModel(
            name='RendezVous',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('heure_debut', models.TimeField()),
                ('heure_fin', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('statut', models.CharField(choices=[('reserve', 'Réservé'), ('termine', 'Terminé'), ('annule', 'Annulé')], default='reserve', max_length=10)),
                ('assistant', models.ForeignKey(blank=True, limit_choices_to={'role': 'ASSISTANT'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rendezvous_assistant', to=settings.AUTH_USER_MODEL)),
                ('medecin', models.ForeignKey(limit_choices_to={'role': 'DOCTOR'}, on_delete=django.db.models.deletion.CASCADE, related_name='rendezvous_medecin', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(limit_choices_to={'role': 'PATIENT'}, on_delete=django.db.models.deletion.CASCADE, related_name='rendezvous_patient', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlageHoraire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('heure_debut', models.TimeField()),
                ('heure_fin', models.TimeField()),
                ('statut', models.CharField(choices=[('reserve', 'Réservé'), ('termine', 'Terminé'), ('grise', 'Grisé')], default='reserve', max_length=10)),
                ('rendez_vous', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rendez_vous.rendezvous')),
            ],
        ),
    ]
