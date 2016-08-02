# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

from promort import settings as pms

import logging
logger = logging.getLogger('promort')


def create_default_groups(apps, schema_editor):
    logger.info('Creating default groups (if needed)')
    Group = apps.get_model('auth', 'Group')
    for group_label, group_data in pms.DEFAULT_GROUPS.iteritems():
        logger.info('Creating default group for "%s"', group_label)
        group, created = Group.objects.get_or_create(name=group_data['name'])
        logger.info('Group "%s" --- Created: %s', group.name, created)


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_default_groups),
    ]
