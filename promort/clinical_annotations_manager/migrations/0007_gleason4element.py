# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-04 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinical_annotations_manager', '0006_auto_20170316_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gleason4Element',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_path', models.TextField()),
                ('area', models.FloatField()),
                ('cellular_density_helper_json', models.TextField()),
                ('cellular_density', models.IntegerField()),
                ('cells_count', models.IntegerField()),
                ('focus_region_annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gleason_4_elements', to='clinical_annotations_manager.FocusRegionAnnotation')),
            ],
        ),
    ]
