# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0005_auto_20160914_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slice',
            name='positive_cores',
        ),
    ]
