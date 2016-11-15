# =======
# WARNING: this script is intended to be only used during the development stage of the project
# to clean completely the database of the application
# =======

from reviews_manager.models import Review, ReviewStep
from slides_manager.models import Case, Slide, SlideQualityControl
from rois_manager.models import Slice

# delete all slices (cores and focus regions will be deleted as well)
Slice.objects.all().delete()

# delete all review steps
ReviewStep.objects.all().delete()

# delete all reviews
Review.objects.all().delete()

# delete all quality control data
SlideQualityControl.objects.all().delete()

# delete all slides
Slide.objects.all().delete()

# ... finally delete all cases
Case.objects.all().delete()
