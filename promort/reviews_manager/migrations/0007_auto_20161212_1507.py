# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def reviews_to_rois_annotations(apps, schema_editor):
    Review = apps.get_model('reviews_manager', 'Review')
    ROIsAnnotation = apps.get_model('reviews_manager', 'ROIsAnnotation')
    ROIsAnnotationStep = apps.get_model('reviews_manager', 'ROIsAnnotationStep')
    for review in Review.objects.all():
        if review.type == 'REVIEW_1':
            rois_annotation = ROIsAnnotation(
                reviewer=review.reviewer,
                case=review.case,
                creation_date=review.creation_date,
                start_date=review.start_date,
                completion_date=review.completion_date
            )
            rois_annotation.save()
            for step in review.steps.all():
                rois_annotations_step = ROIsAnnotationStep(
                    rois_annotation=rois_annotation,
                    slide=step.slide,
                    creation_date=step.creation_date,
                    start_date=step.start_date,
                    completion_date=step.completion_date
                )
                rois_annotations_step.save()


def revers_reviews_to_rois_annotations(apps, schema_editor):
    ROIsAnnotation = apps.get_model('reviews_manager', 'ROIsAnnotation')
    ROIsAnnotationStep = apps.get_model('reviews_manager', 'ROIsAnnotationStep')
    ROIsAnnotationStep.objects.all().delete()
    ROIsAnnotation.objects.all().delete()


def reviews_to_clinical_annotations(apps, schema_editor):
    Review = apps.get_model('reviews_manager', 'Review')
    ROIsAnnotation = apps.get_model('reviews_manager', 'ROIsAnnotation')
    ClinicalAnnotation = apps.get_model('reviews_manager', 'ClinicalAnnotation')
    ClinicalAnnotationStep = apps.get_model('reviews_manager', 'ClinicalAnnotationStep')
    for review in Review.objects.all():
        rois_review = ROIsAnnotation.objects.filter(reviewer=review.reviewer, case=review.case).first()
        clinical_annotation = ClinicalAnnotation(
            reviewer=review.reviewer,
            case=review.case,
            rois_review=rois_review,
            creation_date=review.creation_date,
            start_date=review.start_date,
            completion_date=review.completion_date
        )
        clinical_annotation.save()
        for step in review.steps.all():
            rois_review_step = rois_review.steps.filter(slide=step.slide).first()
            clinical_annotation_step = ClinicalAnnotationStep(
                clinical_annotation=clinical_annotation,
                slide=step.slide,
                rois_review_step=rois_review_step,
                creation_date=step.creation_date,
                start_date=step.start_date,
                completion_date=step.completion_date,
                notes=step.notes
            )
            clinical_annotation_step.save()


def reverse_reviews_to_clinical_annotations(apps, schema_editor):
    ClinicalAnnotation = apps.get_model('reviews_manager', 'ClinicalAnnotation')
    ClinicalAnnotationStep = apps.get_model('reviews_manager', 'ClinicalAnnotationStep')
    ClinicalAnnotationStep.objects.all().delete()
    ClinicalAnnotation.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_manager', '0006_auto_20161212_1611'),
    ]

    operations = [
        migrations.RunPython(reviews_to_rois_annotations, revers_reviews_to_rois_annotations),
        migrations.RunPython(reviews_to_clinical_annotations, reverse_reviews_to_clinical_annotations)
    ]
