# Generated by Django 5.0.6 on 2024-07-25 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0008_alter_chatbotthreads_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchedulerRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.CharField(max_length=300)),
            ],
            options={
                'verbose_name': 'Scheduler Records',
            },
        ),
    ]