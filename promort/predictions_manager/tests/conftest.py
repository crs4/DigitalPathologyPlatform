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

import json

import factory
from django.contrib.auth.models import Group, User
from pytest import fixture
from pytest_factoryboy import register
from shapely.affinity import translate
from shapely.geometry import box


@register
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")


@register
class CaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "slides_manager.Case"

    id = factory.Sequence(lambda n: f"case_{n}")


@register
class SlideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "slides_manager.Slide"

    id = factory.Sequence(lambda n: f"slide_{n}")
    case = factory.SubFactory(CaseFactory)
    image_type = ""


@register
class PredictionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "predictions_manager.Prediction"

    label = factory.Sequence(lambda n: f"prediction_{n}")
    slide = factory.SubFactory(SlideFactory)
    type = "TISSUE"
    omero_id = factory.Sequence(lambda n: n)


@register
class TissueFragmentsCollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "predictions_manager.TissueFragmentsCollection"

    prediction = factory.SubFactory(PredictionFactory)


@register
class TissueFragmentsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "predictions_manager.TissueFragment"

    collection = factory.SubFactory(TissueFragmentsCollectionFactory)
    #  shape_json = '{"coordinates": [[0, 0], [0, 10], [10, 10], [10, 0], [0,0]], "area": 100, "length": 40}'


@fixture
def reviewer():
    user = UserFactory()
    group = Group.objects.get(name="ROIS_MANAGERS")
    group.user_set.add(user)
    return user


@fixture
def fragments_factory():
    def _create_fragments(n: int, collection, rows: int = 1):
        fragments = []

        base_shape = box(0, 0, 10, 10)
        #  base_shape = {
        #      "coordinates": [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
        #      "area": 100,
        #      "length": 40,
        #  }
        for row in range(rows):
            for i in range(n):
                shape = translate(base_shape, 20 * i, 20 * row)
                fragments.append(
                    TissueFragmentsFactory(
                        shape_json=json.dumps(
                            {
                                "coordinates": list(shape.exterior.coords),
                                "area": shape.area,
                                "length": shape.length,
                            }
                        ),
                        collection=collection,
                    )
                )

        return fragments

    return _create_fragments
