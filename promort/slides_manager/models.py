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
from django.utils import timezone


class Laboratory(models.Model):
    label = models.CharField(max_length=30, primary_key=True)

    @staticmethod
    def related_cases_count(obj):
        return len(obj.cases.all())


class Case(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    import_date = models.DateTimeField(auto_now_add=True)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.PROTECT, related_name='cases',
                                   default=None, blank=True, null=True)


class Slide(models.Model):
    id = models.CharField(max_length=25, primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False, related_name='slides')
    import_date = models.DateTimeField(auto_now_add=True)
    omero_id = models.IntegerField(blank=True, null=True,
                                   default=None)
    image_type = models.CharField(max_length=15, blank=True,
                                  null=True)
    image_microns_per_pixel = models.FloatField(default=0.0)


class SlideEvaluation(models.Model):
    from reviews_manager.models import ROIsAnnotationStep

    NOT_ADEQUACY_REASONS_CHOICES = (
        ('BAD_TILES', 'Bad tiles stitching'),
        ('BAD_STAINING', 'Faded staining'),
        ('BAD_FOCUS', 'Non uniform focus'),
        ('DMG_SMP', 'Damaged samples'),
        ('NO_CANCER', 'Non-cancer slide'),
        ('OTHER', 'Other (see notes)')
    )

    STAINING_CHOICES = (
        ('HE', 'H&E'),
        ('TRI', 'Trichrome')
    )

    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False, unique=False)
    rois_annotation_step = models.OneToOneField(ROIsAnnotationStep, on_delete=models.PROTECT,
                                                blank=False, unique=True,
                                                related_name='slide_evaluation')
    staining = models.CharField(max_length=3, choices=STAINING_CHOICES, blank=False)
    adequate_slide = models.BooleanField(blank=False)
    not_adequacy_reason = models.CharField(
        max_length=15, choices=NOT_ADEQUACY_REASONS_CHOICES,
        blank=True, null=True, default=None
    )
    notes = models.TextField(blank=True, null=True)
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    acquisition_date = models.DateTimeField(auto_now_add=True)

    def get_not_adequacy_reason_text(self):
        for choice in self.NOT_ADEQUACY_REASONS_CHOICES:
            if choice[0] == self.not_adequacy_reason:
                return choice[1]

    def get_staining_text(self):
        for choice in self.STAINING_CHOICES:
            if choice[0] == self.staining:
                return choice[1]


class SlidesSet(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    creation_date = models.DateTimeField(default=timezone.now)


class SlidesSetItem(models.Model):
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False, unique=False, null=False)
    slides_set = models.ForeignKey(SlidesSet, on_delete=models.PROTECT,
                                   blank=False, unique=False, null=False,
                                   related_name='items')
    set_label = models.CharField(unique=False, blank=False, null=False,
                                 max_length=20)
    set_index = models.IntegerField(unique=False, blank=True, null=True)

    class Meta:
        unique_together = (
            ('slide', 'slides_set'),
            ('slide', 'slides_set', 'set_label'),
            ('slide', 'slides_set', 'set_index')
        )
