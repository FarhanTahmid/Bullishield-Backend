# Generated by Django 5.0.6 on 2024-07-27 17:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0011_complainproofextractedstrings'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulerrecords',
            name='complain_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='system.usercomplains'),
        ),
    ]
