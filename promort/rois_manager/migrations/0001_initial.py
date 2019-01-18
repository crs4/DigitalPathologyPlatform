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
        ('slides_manager', '0003_auto_20160713_1217'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CellularFocus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=10)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('roi_json', models.TextField()),
                ('length', models.FloatField(default=0.0)),
                ('area', models.FloatField(default=0)),
                ('tumor_area', models.BooleanField()),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Core',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=10)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('roi_json', models.TextField()),
                ('length', models.FloatField(default=0.0)),
                ('area', models.FloatField(default=0.0)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Slice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=10)),
                ('creation_data', models.DateTimeField(auto_now_add=True)),
                ('roi_json', models.TextField()),
                ('total_cores', models.IntegerField(default=0)),
                ('positive_cores', models.IntegerField(default=0)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('slide', models.ForeignKey(related_name='slices', on_delete=django.db.models.deletion.PROTECT, to='slides_manager.Slide')),
            ],
        ),
        migrations.AddField(
            model_name='core',
            name='slice',
            field=models.ForeignKey(related_name='cores', on_delete=django.db.models.deletion.PROTECT, to='rois_manager.Slice'),
        ),
        migrations.AddField(
            model_name='cellularfocus',
            name='core',
            field=models.ForeignKey(related_name='cellular_focuses', on_delete=django.db.models.deletion.PROTECT, to='rois_manager.Core'),
        ),
        migrations.AlterUniqueTogether(
            name='slice',
            unique_together=set([('label', 'slide')]),
        ),
        migrations.AlterUniqueTogether(
            name='core',
            unique_together=set([('label', 'slice')]),
        ),
        migrations.AlterUniqueTogether(
            name='cellularfocus',
            unique_together=set([('label', 'core')]),
        ),
    ]
