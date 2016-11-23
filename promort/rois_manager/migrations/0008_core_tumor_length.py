# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0007_auto_20161020_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='core',
            name='tumor_length',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
