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
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0014_auto_20170609_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewsComparison',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('positive_match', models.NullBooleanField(default=None)),
                ('review_1', models.OneToOneField(related_name='first_review', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ClinicalAnnotationStep')),
                ('review_2', models.OneToOneField(related_name='second_review', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ClinicalAnnotationStep')),
                ('review_3', models.OneToOneField(related_name='gold_standard', null=True, on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='reviews_manager.ClinicalAnnotationStep')),
            ],
        ),
        migrations.AlterField(
            model_name='clinicalannotation',
            name='rois_review',
            field=models.ForeignKey(related_name='clinical_annotations', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ROIsAnnotation'),
        ),
    ]
