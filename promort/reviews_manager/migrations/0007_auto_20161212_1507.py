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


def reverse_reviews_to_rois_annotations(apps, schema_editor):
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
        migrations.RunPython(reviews_to_rois_annotations, reverse_reviews_to_rois_annotations),
        migrations.RunPython(reviews_to_clinical_annotations, reverse_reviews_to_clinical_annotations)
    ]
