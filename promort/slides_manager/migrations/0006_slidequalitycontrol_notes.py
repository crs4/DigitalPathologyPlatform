# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0005_slide_staining'),
    ]

    operations = [
        migrations.AddField(
            model_name='slidequalitycontrol',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
