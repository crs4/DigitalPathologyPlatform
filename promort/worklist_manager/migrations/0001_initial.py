# -*- coding: utf-8 -*-

#  Copyright (c) 2019, CRS4
# 
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

from promort import settings as pms

import logging
logger = logging.getLogger('promort')


def create_default_groups(apps, schema_editor):
    logger.info('Creating default groups (if needed)')
    Group = apps.get_model('auth', 'Group')
    for group_label, group_data in pms.DEFAULT_GROUPS.items():
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
