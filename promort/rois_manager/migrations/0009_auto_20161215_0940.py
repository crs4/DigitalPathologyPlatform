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
