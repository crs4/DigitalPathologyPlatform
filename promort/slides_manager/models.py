from django.db import models


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
                             blank=False)
    import_date = models.DateTimeField(auto_now_add=True)
    omero_id = models.IntegerField(blank=True, null=True,
                                   default=None)
    image_type = models.CharField(max_length=15, blank=False)

    def __unicode__(self):
        return 'Slide %s [img type: %s --- OMERO id: %r]' % (self.id, self.image_type,
                                                             self.omero_id)
