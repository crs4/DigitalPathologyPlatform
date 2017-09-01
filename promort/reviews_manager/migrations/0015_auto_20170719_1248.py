# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0014_auto_20170609_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewsComparison',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('positive_match', models.NullBooleanField(default=None)),
                ('review_1', models.OneToOneField(related_name='first_review', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ClinicalAnnotationStep')),
                ('review_2', models.OneToOneField(related_name='second_review', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ClinicalAnnotationStep')),
                ('review_3', models.OneToOneField(related_name='gold_standard', null=True, on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='reviews_manager.ClinicalAnnotationStep')),
            ],
        ),
        migrations.AlterField(
            model_name='clinicalannotation',
            name='rois_review',
            field=models.ForeignKey(related_name='clinical_annotations', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ROIsAnnotation'),
        ),
    ]
