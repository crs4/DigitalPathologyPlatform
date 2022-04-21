import time
from datetime import datetime
from typing import Union

import pytest
from django.contrib.auth.models import User
from django.test import Client
from reviews_manager.models import (
    AnnotationSession,
    ClinicalAnnotation,
    ClinicalAnnotationStep,
    ROIsAnnotation,
    ROIsAnnotationStep,
    update_annotation_session,
)
from slides_manager.models import Case, Slide
import promort.settings as settings


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def slide(case):
    return Slide.objects.create(case=case)


@pytest.fixture
def rois_annotation(reviewer, case):
    return ROIsAnnotation.objects.create(reviewer=reviewer, case=case)


@pytest.fixture
def clinical_annotation(reviewer, case, rois_annotation, label):
    return ClinicalAnnotation.objects.create(
        label=label, reviewer=reviewer, case=case, rois_review=rois_annotation
    )


@pytest.fixture
def reviewer():
    user = User.objects.create()
    return user


@pytest.fixture
def case():
    return Case.objects.create()


@pytest.fixture
def rois_annotation_step(rois_annotation, slide, label):
    return ROIsAnnotationStep.objects.create(
        label=label, rois_annotation=rois_annotation, slide=slide
    )


@pytest.fixture
def annotation_step(
    annotation_step_cls: Union[ROIsAnnotationStep, ClinicalAnnotationStep],
    rois_annotation,
    rois_annotation_step,
    clinical_annotation,
    slide,
    label,
):
    if annotation_step_cls == ROIsAnnotationStep:
        return rois_annotation_step
    else:
        return ClinicalAnnotationStep.objects.create(
            label=label,
            clinical_annotation=clinical_annotation,
            slide=slide,
            rois_review_step=rois_annotation_step,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "annotation_step_cls", [ROIsAnnotationStep, ClinicalAnnotationStep]
)
@pytest.mark.parametrize("label", ["a0-a0"])
def test_session_create(annotation_step, annotation_step_cls, label):
    now = datetime.now()
    session = update_annotation_session(annotation_step, now)
    assert session.start_time == session.last_update == now
    assert not session.is_expired()

    time.sleep(1.1)
    now_2 = datetime.now()

    session_2 = update_annotation_session(annotation_step, now_2)
    assert session_2.id == session.id
    assert session.last_update < session_2.last_update

    settings.ANNOTATION_SESSION_EXPIRED_TIME = 1
    assert session_2.is_expired()

    now_3 = datetime.now()
    session_3 = update_annotation_session(annotation_step, now_3)
    assert session_3.id != session_2.id

    settings.ANNOTATION_SESSION_EXPIRED_TIME = 1000
    now_4 = datetime.now()
    session_4 = update_annotation_session(annotation_step, now_4)
    assert session_4.id == session_3.id


@pytest.fixture
def update_time():
    return datetime.now().isoformat()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "annotation_step_cls, path",
    [
        (ClinicalAnnotationStep, "clinical_annotations/steps"),
        (ROIsAnnotationStep, "roi_annotations_steps"),
    ],
)
@pytest.mark.parametrize("label", ["a0-a0"])
def test_view_annotation_session(
    client, annotation_step, annotation_step_cls, path, label, update_time
):
    url = f"/api/{path}/{label}/update_session/"

    data = {"update_time": update_time}
    response = client.post(url, data=data)

    assert response.status_code < 300

    resp_json = response.json()
    assert resp_json["start_time"] == update_time
    assert resp_json["last_update"] == update_time


@pytest.mark.django_db
@pytest.mark.parametrize(
    "annotation_step_cls", [ROIsAnnotationStep, ClinicalAnnotationStep]
)
@pytest.mark.parametrize("label", ["a0-a0"])
def test_total_sessions_time(annotation_step, annotation_step_cls, label):
    now = datetime.now()
    update_annotation_session(annotation_step, now)
    assert annotation_step.total_sessions_time() == 0

    time.sleep(1)
    now_2 = datetime.now()
    update_annotation_session(annotation_step, now_2)

    assert round(annotation_step.total_sessions_time(), 3) == round((now_2 - now).total_seconds(), 3)

    settings.ANNOTATION_SESSION_EXPIRED_TIME = 1
    time.sleep(1.1)
    now_3 = datetime.now()
    update_annotation_session(annotation_step, now_3)

    assert round(annotation_step.total_sessions_time(), 3) == round((now_2 - now).total_seconds(), 3)
    time.sleep(1.1)
    now_4 = datetime.now()
    update_annotation_session(annotation_step, now_4)

    assert (
        round(annotation_step.total_sessions_time(), 3)
        == round(((now_4 - now_3) + (now_2 - now)).total_seconds(), 3)
    )
