# Generated by Django 5.1 on 2024-11-15 16:16

import mtechMinorEval.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mtechMinorEval', '0018_remove_activitylog_action_remove_activitylog_faculty_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='ppt',
            field=models.FileField(blank=True, null=True, upload_to='mtechMinorEval/ppts/', validators=[mtechMinorEval.models.validate_file_size]),
        ),
    ]
