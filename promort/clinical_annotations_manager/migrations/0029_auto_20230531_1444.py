# Generated by Django 3.1.13 on 2023-05-31 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinical_annotations_manager', '0028_auto_20221107_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coreannotation',
            name='gleason_group',
            field=models.CharField(choices=[('GG1', 'GRADE_GROUP_1'), ('GG2', 'GRADE_GROUP_2'), ('GG3', 'GRADE_GROUP_3'), ('GG4', 'GRADE_GROUP_4'), ('GG5', 'GRADE_GROUP_5')], default=None, max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='coreannotation',
            name='primary_gleason',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='coreannotation',
            name='secondary_gleason',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
