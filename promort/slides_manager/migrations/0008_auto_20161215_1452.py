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
