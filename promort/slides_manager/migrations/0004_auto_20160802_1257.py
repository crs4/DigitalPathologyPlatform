# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0003_auto_20160713_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slidequalitycontrol',
            name='not_adequacy_reason',
            field=models.CharField(default=None, max_length=10, null=True, blank=True, choices=[(b'BAD_TILES', b'Bad tiles stitching'), (b'BAD_FOCUS', b'Non uniform focus'), (b'DMG_SMP', b'Damaged samples'), (b'OTHER', b'Other (see notes)')]),
        ),
    ]
