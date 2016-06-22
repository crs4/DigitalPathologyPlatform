from django.db import models
from django.contrib.auth.models import User
from slides_manager.models import Case, Slide


class Review(models.Model):
    REVIEW_TYPE = (
        ('REVIEW_1', 'First review'),
        ('REVIEW_2', 'Second review'),
        ('REVIEW_3', 'Third review')
    )

    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)
    type = models.CharField(max_length=8, choices=REVIEW_TYPE,
                            blank=False)

    class Meta:
        unique_together = ('case', 'type')


class ReviewStep(models.Model):
    review = models.ForeignKey(Review, on_delete=models.PROTECT,
                               blank=False)
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(blank=True, null=True,
                                      default=None)
    completion_date = models.DateTimeField(blank=True, null=True,
                                           default=None)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('review', 'slide')
