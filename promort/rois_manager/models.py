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
    creation_start_date = models.DateTimeField(null=True, default=None)
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

    def get_focus_regions(self):
        focus_regions = list()
        for core in self.cores.all():
            focus_regions.extend(core.focus_regions.all())
        return focus_regions


class Core(models.Model):
    label = models.CharField(max_length=25, blank=False)
    slice = models.ForeignKey(Slice, on_delete=models.CASCADE,
                              blank=False, related_name='cores')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    craetion_start_date = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    length = models.FloatField(blank=False, default=0.0)
    area = models.FloatField(blank=False, default=0.0)
    tumor_length = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('label', 'slice')

    def get_total_tumor_area(self):
        total_cancerous_area = 0.0
        for focus_region in self.focus_regions.all():
            if focus_region.is_cancerous_region():
                total_cancerous_area += focus_region.area
        return total_cancerous_area

    def get_normal_tissue_percentage(self):
        total_cancerous_area = self.get_total_tumor_area()
        return ((self.area - total_cancerous_area) / self.area) * 100.0

    def is_positive(self):
        for fr in self.focus_regions.all():
            if fr.is_cancerous_region():
                return True
        return False


class FocusRegion(models.Model):
    TISSUE_STATUS_CHOICES = (
        ('NORMAL', 'Normal'),
        ('STRESSED', 'Stressed'),
        ('TUMOR', 'Tumor')
    )

    label = models.CharField(max_length=40, blank=False)
    core = models.ForeignKey(Core, on_delete=models.CASCADE,
                             blank=False, related_name='focus_regions')
    author = models.ForeignKey(User, on_delete=models.PROTECT,
                               blank=False)
    creation_start_date = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    roi_json = models.TextField(blank=False)
    length = models.FloatField(blank=False, default=0.0)
    area = models.FloatField(blank=False, default=0.0)
    tissue_status = models.CharField(max_length=8, choices=TISSUE_STATUS_CHOICES, blank=False)

    class Meta:
        unique_together = ('label', 'core')

    def get_core_coverage_percentage(self):
        return (self.area / self.core.area) * 100.0

    def is_cancerous_region(self):
        return self.tissue_status == 'TUMOR'

    def is_stressed_region(self):
        return self.tissue_status == 'STRESSED'

    def is_normal_region(self):
        return self.tissue_status == 'NORMAL'
