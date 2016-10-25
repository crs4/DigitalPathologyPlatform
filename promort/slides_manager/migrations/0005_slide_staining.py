# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0004_auto_20160802_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='slide',
            name='staining',
            field=models.CharField(default=None, max_length=5, null=True, blank=True, choices=[(b'HE', b'H&E'), (b'TRI', b'Trichrome')]),
        ),
    ]
