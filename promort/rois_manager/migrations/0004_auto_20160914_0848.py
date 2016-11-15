# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0003_auto_20160913_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cellularfocus',
            name='core',
            field=models.ForeignKey(related_name='cellular_focuses', to='rois_manager.Core'),
        ),
        migrations.AlterField(
            model_name='core',
            name='slice',
            field=models.ForeignKey(related_name='cores', to='rois_manager.Slice'),
        ),
    ]
