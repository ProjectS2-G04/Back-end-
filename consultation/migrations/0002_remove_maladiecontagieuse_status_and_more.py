# Generated by Django 5.1.3 on 2025-04-27 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maladiecontagieuse',
            name='status',
        ),
        migrations.RemoveField(
            model_name='maladiecronique',
            name='status',
        ),
        migrations.AddField(
            model_name='consultation',
            name='test',
            field=models.CharField(choices=[('Regulier', 'Regulier '), ('Automatique', 'Automatique')], default='Regulier', max_length=30),
        ),
    ]
