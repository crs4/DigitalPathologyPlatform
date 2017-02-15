# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def assign_rois_annotation_step(apps, schema_editor):
    ROIsAnnotationStep = apps.get_model('reviews_manager', 'ROIsAnnotationStep')
    SlideQualityControl = apps.get_model('slides_manager', 'SlideQualityControl')

    for qc in SlideQualityControl.objects.all():
        annotation_step = ROIsAnnotationStep.objects.filter(slide=qc.slide).first()
        qc.rois_annotation_step = annotation_step
        qc.save()


def remove_rois_annotation_step(apps, schema_editor):
    SlideQualityControl = apps.get_model('slides_manager', 'SlideQualityControl')

    for qc in SlideQualityControl.objects.all():
        qc.rois_annotation_step = None
        qc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0007_auto_20161215_1503'),
    ]

    operations = [
        migrations.RunPython(assign_rois_annotation_step, remove_rois_annotation_step)
    ]
