# Generated by Django 4.2.7 on 2025-04-03 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DossierMedicale', '0005_dossiermedical_dossier_pdf'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='uploads/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='dossiermedical',
            name='dossier_pdf',
        ),
    ]
