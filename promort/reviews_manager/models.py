from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from slides_manager.models import Case, Slide


class ROIsAnnotation(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)

    class Meta:
        unique_together = ('reviewer', 'case')

    def is_started(self):
        return not(self.start_date is None)

    def is_completed(self):
        return not(self.completion_date is None)

    def can_be_closed(self):
        for rs in self.steps.all():
            if not rs.is_completed():
                return False
        return True


class ROIsAnnotationStep(models.Model):
    rois_annotation = models.ForeignKey(ROIsAnnotation, on_delete=models.PROTECT,
                                        blank=False, related_name='steps')
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)

    class Meta:
        unique_together = ('rois_annotation', 'slide')

    def is_started(self):
        return not(self.start_date is None)

    def is_completed(self):
        return not(self.completion_date is None)


class ClinicalAnnotation(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False)
    rois_review = models.ForeignKey(ROIsAnnotation, on_delete=models.PROTECT,
                                    blank=False)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)

    class Meta:
        unique_together = ('rois_review', 'reviewer')

    def is_started(self):
        return not(self.start_date is None)

    def is_completed(self):
        return not(self.completion_date is None)

    def can_be_started(self):
        return self.rois_review.is_completed()

    def can_be_closed(self):
        for rs in self.steps.all():
            if not rs.is_completed():
                return False
        return True


class ClinicalAnnotationStep(models.Model):
    clinical_annotation = models.ForeignKey(ClinicalAnnotation, on_delete=models.PROTECT,
                                            blank=False, related_name='steps')
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False)
    rois_review_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                         blank=False)
    creation_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)
    notes = models.TextField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ('rois_review_step', 'clinical_annotation')

    def is_started(self):
        return not(self.start_date is None)

    def is_completed(self):
        return not(self.completion_date is None)

    def can_be_started(self):
        return self.clinical_annotation.can_be_started()
