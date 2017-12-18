from django.db import models
from django.contrib.auth.models import User
from slides_manager.models import Slide
from reviews_manager.models import ROIsAnnotationStep


class Slice(models.Model):
    label = models.CharField(max_length=25, blank=False)
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT, blank=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    annotation_step = models.ForeignKey(ROIsAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name='slices')
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    total_cores = models.IntegerField(blank=False, default=0)

    class Meta:
        unique_together = ('label', 'annotation_step')

    def is_positive(self):
        for core in self.cores.all():
            if core.is_positive():
                return True
        return False

    def get_positive_cores_count(self):
        positive_cores_counter = 0
        for core in self.cores.all():
            if core.is_positive():
                positive_cores_counter += 1
        return positive_cores_counter


class Core(models.Model):
    label = models.CharField(max_length=25, blank=False)
    slice = models.ForeignKey(Slice, on_delete=models.CASCADE,
                              blank=False, related_name='cores')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    length = models.FloatField(blank=False, default=0.0)
    area = models.FloatField(blank=False, default=0.0)
    tumor_length = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('label', 'slice')

    def get_normal_tissue_percentage(self):
        total_cancerous_area = 0.0
        for focus_region in self.focus_regions.all():
            if focus_region.cancerous_region:
                total_cancerous_area += focus_region.area
        return ((self.area - total_cancerous_area) / self.area) * 100.0

    def is_positive(self):
        for fr in self.focus_regions.all():
            if fr.cancerous_region:
                return True
        return False


class FocusRegion(models.Model):
    label = models.CharField(max_length=40, blank=False)
    core = models.ForeignKey(Core, on_delete=models.CASCADE,
                             blank=False, related_name='focus_regions')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    length = models.FloatField(blank=False, default=0.0)
    area = models.FloatField(blank=False, default=0.0)
    cancerous_region = models.BooleanField(blank=False)

    class Meta:
        unique_together = ('label', 'core')

    def get_core_coverage_percentage(self):
        return (self.area / self.core.area) * 100.0
