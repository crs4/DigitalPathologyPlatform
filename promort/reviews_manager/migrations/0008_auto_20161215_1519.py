# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0007_auto_20161212_1507'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='review',
            name='case',
        ),
        migrations.RemoveField(
            model_name='review',
            name='reviewer',
        ),
        migrations.AlterUniqueTogether(
            name='reviewstep',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='reviewstep',
            name='review',
        ),
        migrations.RemoveField(
            model_name='reviewstep',
            name='slide',
        ),
        migrations.DeleteModel(
            name='Review',
        ),
        migrations.DeleteModel(
            name='ReviewStep',
        ),
    ]
