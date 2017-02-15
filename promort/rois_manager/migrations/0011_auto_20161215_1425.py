# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0010_auto_20161215_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='core',
            name='annotation_step',
            field=models.ForeignKey(to='reviews_manager.ROIsAnnotationStep', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='focusregion',
            name='annotation_step',
            field=models.ForeignKey(to='reviews_manager.ROIsAnnotationStep', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='slice',
            name='annotation_step',
            field=models.ForeignKey(to='reviews_manager.ROIsAnnotationStep', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
