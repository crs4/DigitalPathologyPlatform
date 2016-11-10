# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0006_remove_slice_positive_cores'),
    ]

    operations = [
        migrations.AlterField(
            model_name='focusregion',
            name='label',
            field=models.CharField(max_length=20),
        ),
    ]
