# Generated by Django 3.1.9 on 2021-09-15 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictions_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='label',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]