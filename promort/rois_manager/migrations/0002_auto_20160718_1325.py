# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cellularfocus',
            old_name='tumor_area',
            new_name='cancerous_region',
        ),
    ]
