# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from uuid import uuid4


def _get_slide_index(slide_label):
    return slide_label.split('-')[-1]


def update_rois_annotations(apps, schema_editor):
    ROIsAnnotations = apps.get_model('reviews_manager', 'ROIsAnnotation')
    for annotation in ROIsAnnotations.objects.all():
        annotation_label = uuid4().hex
        annotation.label = annotation_label
        annotation.save()
        for step in annotation.steps.all():
            slide_index = _get_slide_index(step.slide.id)
            step.label = '%s-%s' % (annotation_label, slide_index)
            step.save()


def update_clinical_annotations(apps, schema_editor):
    ClinicalAnnotation = apps.get_model('reviews_manager', 'ClinicalAnnotation')
    for annotation in ClinicalAnnotation.objects.all():
        if annotation.reviewer == annotation.rois_review.reviewer:
            annotation_label = annotation.rois_review.label
        else:
            annotation_label = uuid4().hex
        annotation.label = annotation_label
        annotation.save()
        for step in annotation.steps.all():
            slide_index = _get_slide_index(step.slide.id)
            step.label = '%s-%s' % (annotation_label, slide_index)
            step.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0011_auto_20170522_1045'),
    ]

    operations = [
        migrations.RunPython(update_rois_annotations),
        migrations.RunPython(update_clinical_annotations),
    ]
