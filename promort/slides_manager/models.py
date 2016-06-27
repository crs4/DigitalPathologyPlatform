from django.db import models
from django.contrib.auth.models import User


class Case(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    import_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Case %s' % self.id

    def _get_slides_list(self):
        return self.slide_set.all()
    slides = property(_get_slides_list)


class Slide(models.Model):
    id = models.CharField(max_length=25, primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False, related_name='slides')
    import_date = models.DateTimeField(auto_now_add=True)
    omero_id = models.IntegerField(blank=True, null=True,
                                   default=None)
    image_type = models.CharField(max_length=15, blank=False)

    def __unicode__(self):
        return 'Slide %s [img type: %s --- OMERO id: %r]' % (self.id, self.image_type,
                                                             self.omero_id)


class SlideQualityControl(models.Model):
    NOT_ADEQUACY_REASONS_CHOICES = (
        ('POOR_IMG', 'Poor image quality'),
        ('DMG_SMP', 'Damaged samples'),
        ('OTHER', 'Other (see notes)')
    )
    slide = models.OneToOneField(Slide, on_delete=models.PROTECT,
                                 blank=False, unique=True,
                                 related_name='quality_control_passed')
    adequate_slide = models.BooleanField(blank=False)
    not_adequacy_reason = models.CharField(
        max_length=8, choices=NOT_ADEQUACY_REASONS_CHOICES,
        blank=True, null=True, default=None
    )
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT,
                                 blank=False)
    acquisition_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.adequate_slide:
            return 'Adequate'
        else:
            return 'Not adequate (reason: %s)' % self.get_not_adequacy_reason_display()
