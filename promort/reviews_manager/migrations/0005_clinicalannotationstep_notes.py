# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0004_auto_20161209_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicalannotationstep',
            name='notes',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
