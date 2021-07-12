#  Copyright (c) 2021, CRS4
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

from slides_manager.models import Slide


class Prediction(models.Model):
    PREDICTION_TYPES = (
        ('TISSUE', 'Tissue recognition'),
        ('TUMOR', 'Tumor detection'),
        ('GLEASON', 'Gleason patterns detection')
    )

    label = models.CharField(max_length=40, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT, blank=False,
                              related_name='predictions')
    type = models.CharField(max_length=7, choices=PREDICTION_TYPES, blank=False, null=False)
    omero_id = models.IntegerField(blank=True, null=True, default=None)
    provenance = models.TextField(blank=True, null=True)


class TissueFragmentsCollection(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.PROTECT, blank=False,
                                   related_name='tissue_fragments')
    creation_date = models.DateTimeField(auto_now_add=True)

    def get_slide(self):
        return self.prediction.slide


class TissueFragment(models.Model):
    collection = models.ForeignKey(TissueFragmentsCollection, on_delete=models.PROTECT, blank=False,
                                   related_name='fragments')
    shape_json = models.TextField(blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
