# Generated by Django 3.1.13 on 2021-11-29 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0021_auto_20210424_1316'),
    ]

    operations = [
        migrations.RenameField(
            model_name='core',
            old_name='creation_start_date',
            new_name='action_start_time',
        ),
        migrations.RenameField(
            model_name='focusregion',
            old_name='creation_start_date',
            new_name='action_start_time',
        ),
        migrations.RenameField(
            model_name='slice',
            old_name='creation_start_date',
            new_name='action_start_time',
        ),
    ]
