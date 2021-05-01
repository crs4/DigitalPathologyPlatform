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
from django.contrib.auth.models import User

from slides_manager.models import SlidesSet


class SharedDataset(models.Model):
    label = models.CharField(max_length=50, blank=False, null=False, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, null=False)
    description = models.TextField(blank=True, null=True, default=None)
    expiry_date = models.DateField(blank=True, null=True, default=None)
    hidden = models.BooleanField(default=False)

    def hide(self):
        if not self.hidden:
            self.hidden=True
            self.save()

    def show(self):
        if set.hidden:
            self.hidden=False
            self.save()

class SharedDatasetItem(models.Model):
    dataset = models.ForeignKey(SharedDataset, on_delete=models.PROTECT, blank=False, null=False,
                                related_name='items')
    slides_set_a = models.ForeignKey(SlidesSet, on_delete=models.PROTECT, blank=False, null=False, unique=False,
                                     related_name='shared_dataset_item_a')
    slides_set_a_label = models.CharField(max_length=50, blank=False, null=False)
    slides_set_b = models.ForeignKey(SlidesSet, on_delete=models.PROTECT, blank=True, null=True, default=None,
                                     related_name='shared_dataset_item_b')
    slides_set_b_label = models.CharField(max_length=50, blank=True, null=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, default=None)

    class Meta:
        unique_together = (
            ('slides_set_a', 'slides_set_b'),
            ('dataset', 'slides_set_a_label'),
            ('dataset', 'slides_set_b_label')
        )
