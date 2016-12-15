# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0007_auto_20161212_1507'),
        ('rois_manager', '0008_core_tumor_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='core',
            name='annotation_step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='reviews_manager.ROIsAnnotationStep', null=True),
        ),
        migrations.AddField(
            model_name='focusregion',
            name='annotation_step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='reviews_manager.ROIsAnnotationStep', null=True),
        ),
        migrations.AddField(
            model_name='slice',
            name='annotation_step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='reviews_manager.ROIsAnnotationStep', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='core',
            unique_together=set([('label', 'slice', 'annotation_step')]),
        ),
        migrations.AlterUniqueTogether(
            name='focusregion',
            unique_together=set([('label', 'core', 'annotation_step')]),
        ),
        migrations.AlterUniqueTogether(
            name='slice',
            unique_together=set([('label', 'slide', 'annotation_step')]),
        ),
    ]
