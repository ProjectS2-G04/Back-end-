# Generated by Django 5.1.7 on 2025-04-18 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rendez_vous', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendezvous',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
