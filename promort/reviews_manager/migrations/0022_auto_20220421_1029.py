# Generated by Django 3.1.9 on 2022-04-21 10:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0021_annotationsession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationsession',
            name='last_update',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]