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
