# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewstep',
            name='review',
            field=models.ForeignKey(related_name='steps', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.Review'),
        ),
    ]
