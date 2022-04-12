# Generated by Django 3.1.13 on 2022-03-24 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('predictions_manager', '0005_auto_20220318_1531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prediction',
            name='provenance',
        ),
        migrations.AddField(
            model_name='provenance',
            name='prediction',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='predictions_manager.prediction'),
        ),
    ]