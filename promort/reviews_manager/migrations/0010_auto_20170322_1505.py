# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-22 15:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0009_auto_20170213_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicalannotationstep',
            name='rois_review_step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clinical_annotation_steps', to='reviews_manager.ROIsAnnotationStep'),
        ),
    ]
