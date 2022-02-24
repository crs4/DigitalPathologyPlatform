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
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from reviews_manager.models import ClinicalAnnotationStep
from rois_manager.models import Slice, Core, FocusRegion


class SliceAnnotation(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    slice = models.ForeignKey(Slice, on_delete=models.PROTECT, blank=False,
                              related_name='clinical_annotations')
    annotation_step = models.ForeignKey(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name='slice_annotations')
    action_start_time = models.DateTimeField(null=True, default=None)
    action_complete_time = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(default=timezone.now)
    high_grade_pin = models.BooleanField(blank=False, null=False, default=False)
    chronic_inflammation = models.BooleanField(blank=False, null=False, default=False)
    acute_inflammation = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
        unique_together = ('slice', 'annotation_step')

    def get_gleason_4_total_area(self):
        gleason_4_total_area = 0.0
        for focus_region in self.slice.get_focus_regions():
            try:
                focus_region_annotation = FocusRegionAnnotation.objects.get(
                    focus_region=focus_region,
                    annotation_step=self.annotation_step
                )
                gleason_4_total_area += focus_region_annotation.get_total_gleason_4_area()
            except FocusRegionAnnotation.DoesNotExist:
                pass
        return gleason_4_total_area

    def get_total_tumor_area(self):
        total_tumor_area = 0.0
        for core in self.slice.cores.all():
            total_tumor_area += core.get_total_tumor_area()
        return total_tumor_area

    def get_gleason_4_percentage(self):
        gleason_4_total_area = self.get_gleason_4_total_area()
        total_tumor_area = self.get_total_tumor_area()
        try:
            return (gleason_4_total_area / total_tumor_area) * 100.0
        except ZeroDivisionError:
            return -1

    def get_action_duration(self):
        if self.action_start_time and self.action_complete_time:
            return (self.action_complete_time-self.action_start_time).total_seconds()
        else:
            return None


class CoreAnnotation(models.Model):
    GLEASON_GROUP_WHO_16 = (
        ('GG1', 'GRADE_GROUP_1'),  # gleason score <= 6
        ('GG2', 'GRADE_GROUP_2'),  # gleason score 3+4=7
        ('GG3', 'GRADE_GROUP_3'),  # gleason score 4+3=7
        ('GG4', 'GRADE_GROUP_4'),  # gleason score 4+4=8 || 3+5=8 || 5+3=8
        ('GG5', 'GRADE_GROUP_5')   # gleason score 9 or 10
    )

    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    core = models.ForeignKey(Core, on_delete=models.PROTECT, blank=False,
                             related_name='clinical_annotations')
    annotation_step = models.ForeignKey(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name='core_annotations')
    action_start_time = models.DateTimeField(null=True, default=None)
    action_complete_time = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(default=timezone.now)
    primary_gleason = models.IntegerField(blank=False)
    secondary_gleason = models.IntegerField(blank=False)
    gleason_group = models.CharField(
        max_length=3, choices=GLEASON_GROUP_WHO_16, blank=False
    )
    gleason_four_percentage = models.IntegerField(blank=False, null=False, default=0,
                                                  validators=[MinValueValidator(0), MaxValueValidator(100)])

    class Meta:
        unique_together = ('core', 'annotation_step')

    def get_gleason_4_total_area(self):
        gleason_4_total_area = 0.0
        for focus_region in self.core.focus_regions.all():
            try:
                focus_region_annotation = FocusRegionAnnotation.objects.get(
                    annotation_step=self.annotation_step,
                    focus_region=focus_region
                )
                gleason_4_total_area += focus_region_annotation.get_total_gleason_4_area()
            except FocusRegionAnnotation.DoesNotExist:
                pass
        return gleason_4_total_area

    def get_total_tumor_area(self):
        return self.core.get_total_tumor_area()

    def get_gleason_4_percentage(self):
        gleason_4_total_area = self.get_gleason_4_total_area()
        total_tumor_area = self.get_total_tumor_area()
        try:
            return (gleason_4_total_area / total_tumor_area) * 100.0
        except ZeroDivisionError:
            return -1

    def get_grade_group_text(self):
        for choice in self.GLEASON_GROUP_WHO_16:
            if choice[0] == self.gleason_group:
                return choice[1]

    def get_action_duration(self):
        if self.action_start_time and self.action_complete_time:
            return (self.action_complete_time-self.action_start_time).total_seconds()
        else:
            return None


class FocusRegionAnnotation(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    focus_region = models.ForeignKey(FocusRegion, on_delete=models.PROTECT,
                                     blank=False, related_name='clinical_annotations')
    annotation_step = models.ForeignKey(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name='focus_region_annotations')
    action_start_time = models.DateTimeField(null=True, default=None)
    action_complete_time = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(default=timezone.now)
    # normal region fields
    atrophy = models.BooleanField(blank=False, null=False, default=False)
    inflammation = models.BooleanField(blank=False, null=False, default=False)
    # cancerous region fields
    perineural_invasion = models.BooleanField(blank=False, null=False, default=False)
    extra_prostatic_extension = models.BooleanField(blank=False, null=False, default=False)
    intraductal_carcinoma = models.BooleanField(blank=False, null=False, default=False)
    ductal_carcinoma = models.BooleanField(blank=False, null=False, default=False)
    poorly_formed_glands = models.BooleanField(blank=False, null=False, default=False)
    cribriform_pattern = models.BooleanField(blank=False, null=False, default=False)
    stroma_rich = models.BooleanField(blank=False, null=False, default=False)
    atypical_intraductal_proliferation = models.BooleanField(blank=False, null=False, default=False)
    mucinous = models.BooleanField(blank=False, null=False, default=False)
    acinar = models.BooleanField(blank=False, null=False, default=False)
    # if acinar == False
    signet_ring_cell = models.BooleanField(blank=False, null=True, default=None)
    sarcomatoid = models.BooleanField(blank=False, null=True, default=None)
    pleomorphic_giant_cell = models.BooleanField(blank=False, null=True, default=None)
    pin_like_carcinoma = models.BooleanField(blank=False, null=True, default=None)
    small_cell = models.BooleanField(blank=False, null=True, default=None)
    neuro_endocrine_differentiation = models.BooleanField(blank=False, null=True, default=None)

    class Meta:
        unique_together = ('focus_region', 'annotation_step')

    def get_total_gleason_4_area(self):
        g4_area = 0
        for g4 in self.get_gleason_4_elements():
            g4_area += g4.area
        return g4_area

    def get_gleason_4_elements(self):
        return self.gleason_elements.filter(gleason_type='G4')

    def get_gleason_4_percentage(self):
        g4_area = self.get_total_gleason_4_area()
        try:
            return (g4_area / self.focus_region.area) * 100.0
        except ZeroDivisionError:
            return -1

    def get_action_duration(self):
        if self.action_start_time and self.action_complete_time:
            return (self.action_complete_time-self.action_start_time).total_seconds()
        else:
            return None


class GleasonElement(models.Model):
    GLEASON_TYPES = (
        ('G1', 'GLEASON 1'),
        ('G2', 'GLEASON 2'),
        ('G3', 'GLEASON 3'),
        ('G4', 'GLEASON 4'),
        ('G5', 'GLEASON 5')
    )
    focus_region_annotation = models.ForeignKey(FocusRegionAnnotation, related_name='gleason_elements',
                                                blank=False, on_delete=models.CASCADE)
    gleason_type = models.CharField(max_length=2, choices=GLEASON_TYPES, blank=False, null=False)
    json_path = models.TextField(blank=False, null=False)
    area = models.FloatField(blank=False, null=False)
    cellular_density_helper_json = models.TextField(blank=True, null=True)
    cellular_density = models.IntegerField(blank=True, null=True)
    cells_count = models.IntegerField(blank=True, null=True)
    action_start_time = models.DateTimeField(null=True, default=None)
    action_complete_time = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(default=timezone.now)

    def get_gleason_type_label(self):
        for choice in self.GLEASON_TYPES:
            if choice[0] == self.gleason_type:
                return choice[1]

    def get_action_duration(self):
        if self.action_start_time and self.action_complete_time:
            return (self.action_complete_time-self.action_start_time).total_seconds()
        else:
            return None
