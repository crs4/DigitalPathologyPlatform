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
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rois_manager', '0004_auto_20160914_0848'),
    ]

    operations = [
        migrations.CreateModel(
            name='FocusRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=10)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('roi_json', models.TextField()),
                ('length', models.FloatField(default=0.0)),
                ('area', models.FloatField(default=0)),
                ('cancerous_region', models.BooleanField()),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('core', models.ForeignKey(related_name='focus_regions', to='rois_manager.Core')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='cellularfocus',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='cellularfocus',
            name='author',
        ),
        migrations.RemoveField(
            model_name='cellularfocus',
            name='core',
        ),
        migrations.DeleteModel(
            name='CellularFocus',
        ),
        migrations.AlterUniqueTogether(
            name='focusregion',
            unique_together=set([('label', 'core')]),
        ),
    ]
