# Generated by Django 5.1.3 on 2025-03-25 14:02

import DossierMedicale.models
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
            name='DossierMedical',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(default='profile_pics/image.jpg', upload_to='profile_pics')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField()),
                ('lieu_naissance', models.CharField(max_length=200)),
                ('adresse', models.TextField()),
                ('numero_telephone', models.CharField(help_text='Entrez un numéro de téléphone de 10 chiffres.', max_length=10, unique=True, validators=[DossierMedicale.models.validate_phone_number])),
                ('email', models.EmailField(help_text="Entrez l'email de l'école (doit se terminer par 'esi-sba.dz').", max_length=254, unique=True, validators=[DossierMedicale.models.validate_email])),
                ('service', models.CharField(blank=True, max_length=100, null=True)),
                ('situation_familiale', models.CharField(blank=True, max_length=100, null=True)),
                ('admission_etablissement', models.BooleanField(default=True)),
                ('taille', models.FloatField(blank=True, null=True)),
                ('poids', models.FloatField(blank=True, null=True)),
                ('frequence_cardiaque', models.FloatField(blank=True, null=True)),
                ('pression_arterielle', models.CharField(blank=True, max_length=20, null=True)),
                ('numero_dossier', models.CharField(max_length=50, unique=True)),
                ('groupe_sanguin', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=3)),
                ('numero_securite_sociale', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('fumeur', models.BooleanField(default=False)),
                ('nombre_cigarettes', models.IntegerField(blank=True, null=True)),
                ('chiqueur', models.BooleanField(default=False)),
                ('nombre_boites_chique', models.IntegerField(blank=True, null=True)),
                ('prise_autre', models.BooleanField(default=False)),
                ('nombre_boites_autre', models.IntegerField(blank=True, null=True)),
                ('age_premiere_prise', models.IntegerField(blank=True, null=True)),
                ('ancien_fumeur', models.BooleanField(default=False)),
                ('nombre_boites_fumeur', models.IntegerField(blank=True, null=True)),
                ('affections_congenitales', models.TextField(blank=True, null=True)),
                ('maladies_generales', models.TextField(blank=True, null=True)),
                ('interventions_chirurgicales', models.TextField(blank=True, null=True)),
                ('reactions_allergiques', models.TextField(blank=True, null=True)),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dossier_medical', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DossierMedicalEnseignant',
            fields=[
                ('dossiermedical_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='DossierMedicale.dossiermedical')),
                ('grade', models.FloatField(max_length=20)),
                ('specialite', models.CharField(max_length=100)),
            ],
            bases=('DossierMedicale.dossiermedical',),
        ),
        migrations.CreateModel(
            name='DossierMedicalEtudian',
            fields=[
                ('dossiermedical_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='DossierMedicale.dossiermedical')),
                ('Fielier', models.CharField(max_length=30)),
                ('Niveau', models.CharField(max_length=20)),
            ],
            bases=('DossierMedicale.dossiermedical',),
        ),
        migrations.CreateModel(
            name='DossierMedicalFonctionnaire',
            fields=[
                ('dossiermedical_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='DossierMedicale.dossiermedical')),
                ('grade', models.FloatField(max_length=20)),
            ],
            bases=('DossierMedicale.dossiermedical',),
        ),
    ]
