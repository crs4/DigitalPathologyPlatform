# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0002_slide_image_microns_per_pixel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slide',
            name='image_microns_per_pixel',
            field=models.FloatField(default=0.0),
        ),
    ]
