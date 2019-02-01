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
