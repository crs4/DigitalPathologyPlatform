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
    gleason_4_percentage = models.FloatField(blank=False, default=0.0)
    gleason_group = models.CharField(
        max_length=3, choices=GLEASON_GROUP_WHO_16, blank=False
    )

    class Meta:
        unique_together = ('core', 'annotation_step')


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
    small_cell_signer_ring = models.BooleanField(blank=False, null=False, default=False)
    hypernephroid_pattern = models.BooleanField(blank=False, null=False, default=False)
    mucinous = models.BooleanField(blank=False, null=False, default=False)
    comedo_necrosis = models.BooleanField(blank=False, null=False, default=False)
    gleason_4_path_json = models.TextField(blank=True)
    gleason_4_area = models.FloatField(default=0)
    cellular_density_helper_json = models.TextField(blank=True)
    cellular_density = models.IntegerField(blank=True)

    class Meta:
        unique_together = ('focus_region', 'annotation_step')
