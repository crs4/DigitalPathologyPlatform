# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('slides_manager', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('type', models.CharField(max_length=8, choices=[(b'REVIEW_1', b'First review'), (b'REVIEW_2', b'Second review'), (b'REVIEW_3', b'Third review')])),
                ('case', models.ForeignKey(to='slides_manager.Case', on_delete=django.db.models.deletion.PROTECT)),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('completion_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('review', models.ForeignKey(to='reviews_manager.Review', on_delete=django.db.models.deletion.PROTECT)),
                ('slide', models.ForeignKey(to='slides_manager.Slide', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='reviewstep',
            unique_together=set([('review', 'slide')]),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set([('case', 'type')]),
        ),
    ]
