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
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0006_slidequalitycontrol_notes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews_manager', '0002_auto_20160622_0917'),
    ]

    operations = [
        migrations.CreateModel(
            name='ROIsAnnotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('case', models.ForeignKey(to='slides_manager.Case', on_delete=django.db.models.deletion.PROTECT)),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='ROIsAnnotationStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('rois_annotation', models.ForeignKey(related_name='steps', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ROIsAnnotation')),
                ('slide', models.ForeignKey(to='slides_manager.Slide', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='roisannotationstep',
            unique_together=set([('rois_annotation', 'slide')]),
        ),
        migrations.AlterUniqueTogether(
            name='roisannotation',
            unique_together=set([('reviewer', 'case')]),
        ),
    ]
