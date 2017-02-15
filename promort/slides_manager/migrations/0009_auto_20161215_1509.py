# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0008_auto_20161215_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slidequalitycontrol',
            name='rois_annotation_step',
            field=models.OneToOneField(related_name='slide_quality_control', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ROIsAnnotationStep'),
        ),
    ]
