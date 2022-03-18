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

import datetime as dt
import json

import factory
from django.contrib.auth.models import Group, User
from pytest import fixture
from pytest_factoryboy import register
from shapely.affinity import translate
from shapely.geometry import box
from slides_manager.models import Case, Slide


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
    image_type = "MIRAX"


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


@fixture
def reviewer():
    user = UserFactory()
    group = Group.objects.get(name="ROIS_MANAGERS")
    group.user_set.add(user)
    return user


def _create_fragments(n: int, collection, rows: int = 1):
    fragments = []

    base_shape = box(0, 0, 10, 10)
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


@fixture
def fragments_factory():

    return _create_fragments


@register
class ROIsAnnotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "reviews_manager.ROIsAnnotation"

    label = factory.Sequence(lambda n: f"annotation_{n}")
    case = factory.SubFactory(CaseFactory)
    reviewer = factory.SubFactory(UserFactory)


class ROIsAnnotationStepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "reviews_manager.ROIsAnnotationStep"

    label = factory.Sequence(lambda n: f"annotation_step_{n}")
    rois_annotation = factory.SubFactory(ROIsAnnotationFactory)
    slide = factory.SubFactory(SlideFactory)


register(ROIsAnnotationStepFactory, "rois_annotation_step")


@fixture
def rois_annotation_steps(reviewer):
    def _create(n_steps, with_fragments):
        steps = []
        for i in range(n_steps):
            slide = SlideFactory()
            step = ROIsAnnotationStepFactory(
                slide=slide, rois_annotation__reviewer=reviewer
            )
            steps.append(step)
            if with_fragments:
                collection = TissueFragmentsCollectionFactory(
                    prediction=PredictionFactory(slide=slide)
                )
                _create_fragments(1, collection)
                with_fragments -= 1

        return steps

    return _create


@fixture
def prediction_data(provenance_data):

    case = Case.objects.create(id="case")
    slide = Slide.objects.create(id="slide", case=case)
    now = dt.datetime.now()
    data = {"label": "label", "slide": slide.id, "type": "TUMOR"}

    if provenance_data:
        data["provenance"] = {
            "model": "model",
            "start_date": now,
            "end_date": now,
            "params": "{}",
        }
    return data
