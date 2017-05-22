# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0012_auto_20170522_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicalannotation',
            name='label',
            field=models.CharField(unique=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='clinicalannotationstep',
            name='label',
            field=models.CharField(unique=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='roisannotation',
            name='label',
            field=models.CharField(unique=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='roisannotationstep',
            name='label',
            field=models.CharField(unique=True, max_length=40),
        ),
    ]
