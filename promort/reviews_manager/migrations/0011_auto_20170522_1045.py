# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0010_auto_20170322_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicalannotation',
            name='label',
            field=models.CharField(max_length=40, unique=True, null=True),
        ),
        migrations.AddField(
            model_name='clinicalannotationstep',
            name='label',
            field=models.CharField(max_length=40, unique=True, null=True),
        ),
        migrations.AddField(
            model_name='roisannotation',
            name='label',
            field=models.CharField(max_length=40, unique=True, null=True),
        ),
        migrations.AddField(
            model_name='roisannotationstep',
            name='label',
            field=models.CharField(max_length=40, unique=True, null=True),
        ),
    ]
