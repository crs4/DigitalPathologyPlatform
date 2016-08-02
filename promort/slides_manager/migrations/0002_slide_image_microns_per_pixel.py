# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='slide',
            name='image_microns_per_pixel',
            field=models.IntegerField(default=0),
        ),
    ]
