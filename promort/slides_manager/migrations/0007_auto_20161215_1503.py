# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0007_auto_20161212_1507'),
        ('slides_manager', '0006_slidequalitycontrol_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='slidequalitycontrol',
            name='rois_annotation_step',
            field=models.OneToOneField(related_name='slide_quality_control', null=True, on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='reviews_manager.ROIsAnnotationStep'),
        ),
        migrations.AlterField(
            model_name='slidequalitycontrol',
            name='slide',
            field=models.ForeignKey(related_name='quality_control_passed', on_delete=django.db.models.deletion.PROTECT, to='slides_manager.Slide'),
        ),
    ]
