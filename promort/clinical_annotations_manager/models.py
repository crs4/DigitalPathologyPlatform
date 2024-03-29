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
from reviews_manager.models import ClinicalAnnotationStep
from rois_manager.models import Slice, Core, FocusRegion

from collections import Counter


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
    pah = models.BooleanField(blank=False, null=False, default=False)
    chronic_inflammation = models.BooleanField(blank=False, null=False, default=False)
    acute_inflammation = models.BooleanField(blank=False, null=False, default=False)
    periglandular_inflammation = models.BooleanField(blank=False, null=False, default=False)
    intraglandular_inflammation = models.BooleanField(blank=False, null=False, default=False)
    stromal_inflammation = models.BooleanField(blank=False, null=False, default=False)

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
    primary_gleason = models.IntegerField(null=True, default=None)
    secondary_gleason = models.IntegerField(null=True, default=None)
    gleason_group = models.CharField(
        max_length=3, choices=GLEASON_GROUP_WHO_16, null=True, default=None
    )
    # acquire ONLY if at least one Cribriform Pattern (under GleasonPattern type 4) exists
    nuclear_grade_size = models.CharField(max_length=1, null=True, default=None)
    intraluminal_acinar_differentiation_grade = models.CharField(max_length=1, null=True, default=None)
    intraluminal_secretions = models.BooleanField(null=True, default=None)
    central_maturation = models.BooleanField(null=True, default=None)
    extra_cribriform_gleason_score = models.CharField(max_length=11, null=True, default=None)
    # stroma
    predominant_rsg = models.CharField(max_length=1, null=True, default=None)
    highest_rsg = models.CharField(max_length=1, null=True, default=None)
    rsg_within_highest_grade_area = models.CharField(max_length=1, null=True, default=None)
    rsg_in_area_of_cribriform_morphology = models.CharField(max_length=1, null=True, default=None)
    # other
    perineural_invasion = models.BooleanField(null=True, default=None)
    perineural_growth_with_cribriform_patterns = models.BooleanField(null=True, default=None)
    extraprostatic_extension = models.BooleanField(null=True, default=None)

    class Meta:
        unique_together = ('core', 'annotation_step')

    def _get_gleason_elements(self):
        gleason_elements = list()
        for fr in self.core.focus_regions.all():
            gleason_elements.extend(
                GleasonPattern.objects.filter(
                    focus_region = fr,
                    annotation_step = self.annotation_step
                ).all()
            )
        return gleason_elements
    
    def _get_gleason_coverage(self):
        g_elems = self._get_gleason_elements()
        total_gleason_area = 0
        gleason_patterns_area = Counter()
        for g_el in g_elems:
            total_gleason_area += g_el.area
            gleason_patterns_area[g_el.gleason_type] += g_el.area
        gleason_coverage = dict()
        for gp, gpa in gleason_patterns_area.items():
            gleason_coverage[gp] = (100 * gpa/total_gleason_area)
        return gleason_coverage
    
    def _get_primary_and_secondary_gleason(self):
        gleason_coverage = self._get_gleason_coverage()
        if len(gleason_coverage) == 0:
            return None, None
        primary_gleason = max(gleason_coverage, key=gleason_coverage.get)
        gleason_coverage.pop(primary_gleason)
        if len(gleason_coverage) == 0:
            secondary_gleason = primary_gleason
        else:
            secondary_gleason = max(gleason_coverage)
        return primary_gleason, secondary_gleason

    def get_primary_gleason(self):
        if self.primary_gleason is None:
            primary_gleason, _ = self._get_primary_and_secondary_gleason()
            return primary_gleason
        else:
            return self.primary_gleason
    
    def get_secondary_gleason(self):
        if self.secondary_gleason is None:
            _, secondary_gleason = self._get_primary_and_secondary_gleason()
            return secondary_gleason
        else:
            return self.secondary_gleason
    
    def get_gleason_group(self):
        if self.gleason_group is None:
            primary_gleason, secondary_gleason = self._get_primary_and_secondary_gleason()
            gleason_score = int(primary_gleason.replace('G', '')) + int(secondary_gleason.replace('G', ''))
            if gleason_score <= 6:
                return 'GG1'
            elif gleason_score == 7:
                if primary_gleason == 'G3':
                    return 'GG2'
                else:
                    return 'GG3'
            elif gleason_score == 8:
                return 'GG4'
            else:
                return 'GG5'
        else:
            return self.gleason_group

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
        gleason_group = self.get_gleason_group()
        for choice in self.GLEASON_GROUP_WHO_16:
            if choice[0] == gleason_group:
                return choice[1]
    
    def get_gleason_patterns_details(self):
        gleason_elements = self._get_gleason_elements()
        gleason_total_areas = Counter()
        gleason_shapes = dict()
        for ge in gleason_elements:
            gleason_total_areas[ge.gleason_type] += ge.area
            gleason_shapes.setdefault(ge.gleason_type, []).append(ge.label)
        gleason_coverage = self._get_gleason_coverage()
        gleason_details = {}
        for gtype in gleason_shapes.keys():
            gleason_details[gtype] = {
                "shapes": gleason_shapes[gtype],
                "total_area": gleason_total_areas[gtype],
                "total_coverage": round(gleason_coverage[gtype], 2)
            }
        return gleason_details

    def get_action_duration(self):
        if self.action_start_time and self.action_complete_time:
            return (self.action_complete_time-self.action_start_time).total_seconds()
        else:
            return None

    def get_largest_confluent_sheet(self):
        # TODO: get largest cribriform object among all Gleason 4 elements of a core
        return None

    def get_total_cribriform_area(self):
        # TODO: sum of all cribriform objects defined on a core
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
    # cancerous region fields
    perineural_involvement = models.BooleanField(blank=False, null=False, default=False)
    intraductal_carcinoma = models.BooleanField(blank=False, null=False, default=False)
    ductal_carcinoma = models.BooleanField(blank=False, null=False, default=False)
    poorly_formed_glands = models.BooleanField(blank=False, null=False, default=False)
    cribriform_pattern = models.BooleanField(blank=False, null=False, default=False)
    small_cell_signet_ring = models.BooleanField(blank=False, null=False, default=False)
    hypernephroid_pattern = models.BooleanField(blank=False, null=False, default=False)
    mucinous = models.BooleanField(blank=False, null=False, default=False)
    comedo_necrosis = models.BooleanField(blank=False, null=False, default=False)
    # stressed region fields
    inflammation = models.BooleanField(blank=False, null=False, default=False)
    pah = models.BooleanField(blank=False, null=False, default=False)
    atrophic_lesions = models.BooleanField(blank=False, null=False, default=False)
    adenosis = models.BooleanField(blank=False, null=False, default=False)
    # ---
    cellular_density_helper_json = models.TextField(blank=True, null=True)
    cellular_density = models.IntegerField(blank=True, null=True)
    cells_count = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('focus_region', 'annotation_step')

    def get_gleason_elements(self):
        gleason_elements_map = dict()
        for gp in self.annotation_step.gleason_annotations.filter(focus_region=self.focus_region).all():
            gleason_elements_map.setdefault(gp.gleason_type, []).append(gp)
        return gleason_elements_map

    def get_gleason_4_elements(self):
        return self.get_gleason_elements().get("G4", [])

    def get_total_gleason_area(self, gleason_pattern):
        gleason_area = 0
        for g in self.get_gleason_elements().get(gleason_pattern, []):
            gleason_area += g.area
        return gleason_area

    def get_total_gleason_4_area(self):
        g4_area = 0
        for g4 in self.get_gleason_4_elements():
            g4_area += g4.area
        return g4_area

    def get_gleason_percentage(self, gleason_pattern):
        gleason_area = self.get_total_gleason_area(gleason_pattern)
        try:
            return (gleason_area / self.focus_region.area) * 100.0
        except ZeroDivisionError:
            return -1

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


class GleasonPattern(models.Model):
    GLEASON_TYPES = (
        ('G3', 'GLEASON 3'),
        ('G4', 'GLEASON 4'),
        ('G5', 'GLEASON 5'),
        ('LG', 'LEGACY')
    )
    label = models.CharField(max_length=25, blank=False)
    focus_region = models.ForeignKey(FocusRegion, related_name="gleason_patterns", blank=False,
                                     on_delete=models.PROTECT)
    annotation_step = models.ForeignKey(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name="gleason_annotations")
    author = models.ForeignKey(User, blank=False, on_delete=models.PROTECT)
    gleason_type = models.CharField(max_length=2, choices=GLEASON_TYPES, blank=False, null=False)
    roi_json = models.TextField(blank=False, null=False)
    details_json = models.TextField(blank=True, null=True)
    area = models.FloatField(blank=False, null=False)
    action_start_time = models.DateTimeField(null=True, default=None)
    action_complete_time = models.DateTimeField(null=True, default=None)
    creation_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('label', 'annotation_step')

    def get_gleason_type_label(self):
        for choice in self.GLEASON_TYPES:
            if choice[0] == self.gleason_type:
                return choice[1]

    def get_action_duration(self):
        if self.action_start_time and self.action_complete_time:
            return (self.action_complete_time-self.action_start_time).total_seconds()
        else:
            return None


class GleasonPatternSubregion(models.Model):
    gleason_pattern = models.ForeignKey(GleasonPattern, related_name="subregions", blank=False,
                                        on_delete=models.CASCADE)
    label = models.CharField(max_length=25, blank=False)
    roi_json = models.TextField(blank=False, null=False)
    area = models.FloatField(blank=False, null=False)
    details_json = models.TextField(blank=True, null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
