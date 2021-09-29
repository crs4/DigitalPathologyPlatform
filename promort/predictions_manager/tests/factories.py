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

import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")


class CaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "slides_manager.Case"

    id = factory.Sequence(lambda n: f"case_{n}")


class SlideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "slides_manager.Slide"

    id = factory.Sequence(lambda n: f"slide_{n}")
    case = factory.SubFactory(CaseFactory)
    image_type = ""


class PredictionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "predictions_manager.Prediction"

    label = factory.Sequence(lambda n: f"prediction_{n}")
    slide = factory.SubFactory(SlideFactory)
    type = "TISSUE"
    omero_id = factory.Sequence(lambda n: n)


class TissueFragmentsCollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "predictions_manager.TissueFragmentsCollection"

    prediction = factory.SubFactory(PredictionFactory)


class TissueFragmentsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "predictions_manager.TissueFragment"

    collection = factory.SubFactory(TissueFragmentsCollectionFactory)
    shape_json = '{"coordinates": []}'
