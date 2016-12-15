from django.db import models
from django.contrib.auth.models import User
from slides_manager.models import Slide
from reviews_manager.models import ROIsAnnotationStep


class Slice(models.Model):
    label = models.CharField(max_length=10, blank=False)
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False, related_name='slices')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    annotation_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                        blank=True, null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    total_cores = models.IntegerField(blank=False, default=0)

    class Meta:
        unique_together = ('label', 'slide', 'annotation_step')


class Core(models.Model):
    label = models.CharField(max_length=10, blank=False)
    slice = models.ForeignKey(Slice, on_delete=models.CASCADE,
                              blank=False, related_name='cores')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    annotation_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                        blank=True, null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    length = models.FloatField(blank=False, default=0.0)
    area = models.FloatField(blank=False, default=0.0)
    tumor_length = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('label', 'slice', 'annotation_step')


class FocusRegion(models.Model):
    label = models.CharField(max_length=20, blank=False)
    core = models.ForeignKey(Core, on_delete=models.CASCADE,
                             blank=False, related_name='focus_regions')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    annotation_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                        blank=True, null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    length = models.FloatField(blank=False, default=0.0)
    area = models.FloatField(blank=False, default=0.0)
    cancerous_region = models.BooleanField(blank=False)

    class Meta:
        unique_together = ('label', 'core', 'annotation_step')
