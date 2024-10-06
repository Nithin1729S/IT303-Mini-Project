# Generated by Django 5.1 on 2024-10-05 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtechMinorEval', '0017_activitylog_isadmin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitylog',
            name='action',
        ),
        migrations.RemoveField(
            model_name='activitylog',
            name='faculty',
        ),
        migrations.RemoveField(
            model_name='activitylog',
            name='isadmin',
        ),
        migrations.RemoveField(
            model_name='activitylog',
            name='project',
        ),
        migrations.RemoveField(
            model_name='activitylog',
            name='student',
        ),
        migrations.AddField(
            model_name='activitylog',
            name='activity',
            field=models.TextField(blank=True, null=True),
        ),
    ]