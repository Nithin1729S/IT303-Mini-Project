# Generated by Django 5.1 on 2024-10-04 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtechMinorEval', '0016_activitylog'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitylog',
            name='isadmin',
            field=models.BooleanField(default=False),
        ),
    ]
