# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def assign_rois_annotation_step(apps, schema_editor):
    ROIsAnnotationStep = apps.get_model('reviews_manager', 'ROIsAnnotationStep')

    annotation_steps = ROIsAnnotationStep.objects.all()
    for step in annotation_steps:
        slide = step.slide
        for slice in slide.slices.all():
            slice.annotation_step = step
            slice.save()
            for core in slice.cores.all():
                core.annotation_step = step
                core.save()
                for focus_region in core.focus_regions.all():
                    focus_region.annotation_step = step
                    focus_region.save()


def remove_rois_annotation_step(apps, schema_editor):
    Slice = apps.get_model('rois_manager', 'Slice')

    for slice in Slice.objects.all():
        slice.annotation_step = None
        slice.save()
        for core in slice.cores.all():
            core.annotation_step = None
            core.save()
            for focus_region in core.focus_regions.all():
                focus_region.annotation_step = None
                focus_region.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rois_manager', '0009_auto_20161215_0940'),
    ]

    operations = [
        migrations.RunPython(assign_rois_annotation_step, remove_rois_annotation_step)
    ]
