# -*- coding: utf-8 -*-

#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals

from django.db import migrations

from uuid import uuid4


def _get_slide_index(slide_label):
    return slide_label.split('-')[-1]


def update_rois_annotations(apps, schema_editor):
    ROIsAnnotation = apps.get_model('reviews_manager', 'ROIsAnnotation')
    for annotation in ROIsAnnotation.objects.all():
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
