# Generated by Django 5.0.6 on 2024-07-25 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0009_schedulerrecords'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulerrecords',
            name='execution_status',
            field=models.BooleanField(default=False),
        ),
    ]
