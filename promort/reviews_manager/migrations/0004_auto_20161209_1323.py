# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '0006_slidequalitycontrol_notes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews_manager', '0003_auto_20161209_1004'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClinicalAnnotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('case', models.ForeignKey(to='slides_manager.Case', on_delete=django.db.models.deletion.PROTECT)),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('rois_review', models.ForeignKey(to='reviews_manager.ROIsAnnotation', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='ClinicalAnnotationStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('clinical_annotation', models.ForeignKey(related_name='steps', on_delete=django.db.models.deletion.PROTECT, to='reviews_manager.ClinicalAnnotation')),
                ('rois_review_step', models.ForeignKey(to='reviews_manager.ROIsAnnotationStep', on_delete=django.db.models.deletion.PROTECT)),
                ('slide', models.ForeignKey(to='slides_manager.Slide', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='clinicalannotationstep',
            unique_together=set([('rois_review_step', 'clinical_annotation')]),
        ),
        migrations.AlterUniqueTogether(
            name='clinicalannotation',
            unique_together=set([('rois_review', 'reviewer')]),
        ),
    ]
