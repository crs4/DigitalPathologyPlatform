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

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from django.utils import timezone
from predictions_manager.models import Prediction
from slides_manager.models import Case, Slide


class ROIsAnnotation(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False, related_name='roi_annotations')
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)

    def is_started(self):
        return not self.start_date is None

    def is_completed(self):
        return not self.completion_date is None

    def can_be_closed(self):
        for rs in self.steps.all():
            if not rs.is_completed():
                return False
        return True

    def reopen(self):
        self.completion_date = None
        self.save()

    def completed_steps_count(self):
        counter = 0
        for step in self.steps.all():
            if step.is_completed():
                counter += 1
        return counter

    def clinical_annotations_completed(self):
        for annotation in self.clinical_annotations.all():
            if not annotation.is_completed():
                return False
        return True


class ROIsAnnotationStep(models.Model):
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
    rois_annotation = models.ForeignKey(ROIsAnnotation, on_delete=models.PROTECT,
                                        blank=False, related_name='steps')
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False, related_name='roi_annotations')
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)
    sessions = GenericRelation("AnnotationSession")

    class Meta:
        unique_together = ('rois_annotation', 'slide')

    @property
    def cores(self):
        cores = []
        for slice in self.slices.all():
            cores.extend(slice.cores.all())
        return cores

    @property
    def focus_regions(self):
        focus_regions = []
        for core in self.cores:
            focus_regions.extend(core.focus_regions.all())
        return focus_regions

    def is_started(self):
        return not self.start_date is None

    def is_completed(self):
        return not self.completion_date is None

    def has_reopen_permission(self, username):
        return self.rois_annotation.reviewer.username == username

    def can_reopen(self):
        if not self.is_completed():
            return False
        if not self.slide_evaluation.adequate_slide:
            return False
        for cs in self.clinical_annotation_steps.all():
            if cs.label != self.label and cs.is_started():
                return False
        return True

    def reopen(self):
        if self.can_reopen():
            for cs in self.clinical_annotation_steps.all():
                cs.reopen()
            if self.rois_annotation.is_completed():
                self.rois_annotation.reopen()
            self.completion_date = None
            self.save()
        else:
            raise IntegrityError('ROIs annotation step can\'t be reopened')

    def is_positive(self):
        for slice in self.slices.all():
            if slice.is_positive():
                return True
        return False


class ClinicalAnnotation(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False, related_name='clinical_annotations')
    rois_review = models.ForeignKey(ROIsAnnotation, on_delete=models.PROTECT,
                                    blank=False, related_name='clinical_annotations')
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)

    class Meta:
        unique_together = ('rois_review', 'reviewer')

    def is_started(self):
        return not self.start_date is None

    def is_completed(self):
        return not self.completion_date is None

    def can_be_started(self):
        return self.rois_review.is_completed()

    def can_be_closed(self):
        for rs in self.steps.all():
            if not rs.is_completed():
                return False
        return True

    def reopen(self):
        if self.is_completed():
            self.completion_date = None
            self.save()

    def completed_steps_count(self):
        counter = 0
        for step in self.steps.all():
            if step.is_completed():
                counter += 1
        return counter


class ClinicalAnnotationStep(models.Model):
    REJECTION_REASONS_CHOICES = (
        ('BAD_QUALITY', 'Bad image quality'),
        ('BAD_ROIS', 'Wrong or inaccurate ROIs'),
        ('OTHER', 'Other (see notes)')
    )

    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
    clinical_annotation = models.ForeignKey(ClinicalAnnotation, on_delete=models.PROTECT,
                                            blank=False, related_name='steps')
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False, related_name='clinical_annotations')
    rois_review_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                         blank=False, related_name='clinical_annotation_steps')
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)
    rejected = models.BooleanField(default=False)
    rejection_reason = models.CharField(
        max_length=20, choices=REJECTION_REASONS_CHOICES,
        blank=True, null=True, default=None
    )
    notes = models.TextField(blank=True, null=True, default=None)
    sessions = GenericRelation("AnnotationSession")

    class Meta:
        unique_together = ('rois_review_step', 'clinical_annotation')

    def is_started(self):
        return not self.start_date is None

    def is_completed(self):
        return not self.completion_date is None

    def can_be_started(self):
        return self.clinical_annotation.can_be_started()

    def reopen(self, delete_annotations=True):
        if self.is_completed():
            if delete_annotations:
                for fr_ann in self.focus_region_annotations.all():
                    fr_ann.delete()
                for c_ann in self.core_annotations.all():
                    c_ann.delete()
                for s_ann in self.slice_annotations.all():
                    s_ann.delete()
                self.start_date = None
            self.completion_date = None
            self.save()
            self.clinical_annotation.reopen()

    def get_rejection_reason_text(self):
        for choice in self.REJECTION_REASONS_CHOICES:
            if choice[0] == self.rejection_reason:
                return choice[1]


class ReviewsComparison(models.Model):
    review_1 = models.OneToOneField(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                    blank=False, null=False, related_name='first_review')
    review_2 = models.OneToOneField(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                    blank=False, null=False, related_name='second_review')
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    completion_date = models.DateTimeField(blank=True, null=True, default=None)
    positive_match = models.BooleanField(blank=True, null=True, default=None)
    positive_quality_control = models.BooleanField(blank=True, null=True, default=None)
    review_3 = models.OneToOneField(ClinicalAnnotationStep, on_delete=models.PROTECT, blank=True,
                                    null=True, default=None, related_name='gold_standard')

    def can_be_started(self):
        if self.is_started() or self.is_completed():
            return False
        return self.review_1.clinical_annotation.is_completed() and \
               self.review_2.clinical_annotation.is_completed()

    def is_started(self):
        return not self.start_date is None

    def is_evaluation_pending(self):
        return self.positive_match is None

    def is_completed(self):
        return not self.completion_date is None

    def link_review_3(self, review_obj):
        self.review_3 = review_obj
        self.save()

    def close(self, positive_match, positive_quality_control):
        self.positive_match = positive_match
        self.positive_quality_control = positive_quality_control
        self.completion_date = datetime.now()
        self.save()

    def linked_reviews_completed(self):
        completed = self.review_1.clinical_annotation.is_completed() \
                    and self.review_2.clinical_annotation.is_completed()
        if self.review_3 is not None:
            return completed and self.review_3.clinical_annotation.is_completed()
        else:
            return completed

    def get_case(self):
        return self.review_1.clinical_annotation.case

    def get_slide(self):
        return self.review_1.slide


class PredictionReview(models.Model):
    label = models.CharField(unique=True, blank=False, null=False, max_length=50)
    prediction = models.ForeignKey(Prediction, on_delete=models.PROTECT,
                                   blank=False, related_name='reviews')
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT, blank=False,
                              related_name='prediction_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True, default=None)
    completion_date = models.DateTimeField(blank=True, null=True, default=None)

    def is_started(self):
        return not self.start_date is None

    def is_completed(self):
        return not self.completion_date is None

    def reopen(self):
        self.completion_date = None
        self.save()


class AnnotationSession(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    start_time = models.DateTimeField(default=timezone.now)
    last_update = models.DateTimeField()
