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
