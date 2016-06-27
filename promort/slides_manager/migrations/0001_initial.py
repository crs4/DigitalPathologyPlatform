# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('import_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.CharField(max_length=25, serialize=False, primary_key=True)),
                ('import_date', models.DateTimeField(auto_now_add=True)),
                ('omero_id', models.IntegerField(default=None, null=True, blank=True)),
                ('image_type', models.CharField(max_length=15)),
                ('case', models.ForeignKey(related_name='slides', on_delete=django.db.models.deletion.PROTECT, to='slides_manager.Case')),
            ],
        ),
        migrations.CreateModel(
            name='SlideQualityControl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('adequate_slide', models.BooleanField()),
                ('not_adequacy_reason', models.CharField(default=None, max_length=8, null=True, blank=True, choices=[(b'POOR_IMG', b'Poor image quality'), (b'DMG_SMP', b'Damaged samples'), (b'OTHER', b'Other (see notes)')])),
                ('acquisition_date', models.DateTimeField(auto_now_add=True)),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('slide', models.OneToOneField(related_name='quality_control_passed', on_delete=django.db.models.deletion.PROTECT, to='slides_manager.Slide')),
            ],
        ),
    ]
