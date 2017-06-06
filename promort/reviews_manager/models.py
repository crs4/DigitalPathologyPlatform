from django.db import models, IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User
from slides_manager.models import Case, Slide


class ROIsAnnotation(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
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

    def reopen(self):
        self.completion_date = None
        self.save()


class ROIsAnnotationStep(models.Model):
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
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

    def can_reopen(self):
        if not self.is_completed():
            return False
        if not self.slide_quality_control.adequate_slide:
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


class ClinicalAnnotation(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
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
    label = models.CharField(unique=True, blank=False, null=False,
                             max_length=40)
    clinical_annotation = models.ForeignKey(ClinicalAnnotation, on_delete=models.PROTECT,
                                            blank=False, related_name='steps')
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False)
    rois_review_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                         blank=False, related_name='clinical_annotation_steps')
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

    def reopen(self):
        for fr_ann in self.focus_region_annotations.all():
            fr_ann.delete()
        for c_ann in self.core_annotations.all():
            c_ann.delete()
        for s_ann in self.slice_annotations.all():
            s_ann.delete()
        self.completion_date = None
        self.start_date = None
        self.save()
