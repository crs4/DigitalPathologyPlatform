from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from reviews_manager.models import ClinicalAnnotationStep
from rois_manager.models import Slice, Core, FocusRegion


class SliceAnnotation(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    slice = models.ForeignKey(Slice, on_delete=models.PROTECT, blank=False,
                              related_name='clinical_annotations')
    annotation_step = models.ForeignKey(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name='slice_annotations')
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
    creation_date = models.DateTimeField(default=timezone.now)
    primary_gleason = models.IntegerField(blank=False)
    secondary_gleason = models.IntegerField(blank=False)
    gleason_group = models.CharField(
        max_length=3, choices=GLEASON_GROUP_WHO_16, blank=False
    )

    class Meta:
        unique_together = ('core', 'annotation_step')

    def get_gleason_4_percentage(self):
        gleason_4_total_area = 0.0
        for focus_region in self.core.focus_regions.all():
            try:
                focus_region_annotation = FocusRegionAnnotation.objects.get(
                    annotation_step=self.annotation_step,
                    focus_region=focus_region
                )
                for gleason_element in focus_region_annotation.gleason_elements.all():
                    if gleason_element.gleason_type == 'G4':
                        gleason_4_total_area += gleason_element.area
            except FocusRegionAnnotation.DoesNotExist:
                pass
        try:
            return (gleason_4_total_area / self.core.area) * 100.0
        except ZeroDivisionError:
            return -1

    def get_grade_group_text(self):
        for choice in self.GLEASON_GROUP_WHO_16:
            if choice[0] == self.gleason_group:
                return choice[1]


class FocusRegionAnnotation(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    focus_region = models.ForeignKey(FocusRegion, on_delete=models.PROTECT,
                                     blank=False, related_name='clinical_annotations')
    annotation_step = models.ForeignKey(ClinicalAnnotationStep, on_delete=models.PROTECT,
                                        blank=False, related_name='focus_region_annotations')
    creation_date = models.DateTimeField(default=timezone.now)
    perineural_involvement = models.BooleanField(blank=False, null=False, default=False)
    intraductal_carcinoma = models.BooleanField(blank=False, null=False, default=False)
    ductal_carcinoma = models.BooleanField(blank=False, null=False, default=False)
    poorly_formed_glands = models.BooleanField(blank=False, null=False, default=False)
    cribriform_pattern = models.BooleanField(blank=False, null=False, default=False)
    small_cell_signet_ring = models.BooleanField(blank=False, null=False, default=False)
    hypernephroid_pattern = models.BooleanField(blank=False, null=False, default=False)
    mucinous = models.BooleanField(blank=False, null=False, default=False)
    comedo_necrosis = models.BooleanField(blank=False, null=False, default=False)
    cellular_density_helper_json = models.TextField(blank=True, null=True)
    cellular_density = models.IntegerField(blank=True, null=True)
    cells_count = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('focus_region', 'annotation_step')

    def get_gleason_4_elements(self):
        return self.gleason_elements.filter(gleason_type='G4')

    def get_gleason_4_percentage(self):
        g4_area = 0
        for g4 in self.get_gleason_4_elements():
            g4_area += g4.area
        try:
            return (g4_area / self.focus_region.area) * 100.0
        except ZeroDivisionError:
            return -1


class GleasonElement(models.Model):
    GLEASON_TYPES = (
        ('G1', 'GLEASON_1'),
        ('G2', 'GLEASON_2'),
        ('G3', 'GLEASON_3'),
        ('G4', 'GLEASON_4'),
        ('G5', 'GLEASON_5')
    )
    focus_region_annotation = models.ForeignKey(FocusRegionAnnotation, related_name='gleason_elements',
                                                blank=False, on_delete=models.CASCADE)
    gleason_type = models.CharField(max_length=2, choices=GLEASON_TYPES, blank=False, null=False)
    json_path = models.TextField(blank=False, null=False)
    area = models.FloatField(blank=False, null=False)
    cellular_density_helper_json = models.TextField(blank=True, null=True)
    cellular_density = models.IntegerField(blank=True, null=True)
    cells_count = models.IntegerField(blank=True, null=True)