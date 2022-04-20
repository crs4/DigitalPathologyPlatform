import time
from datetime import datetime
from typing import Union

import pytest
from django.contrib.auth.models import User
from reviews_manager.models import (AnnotationSession, ClinicalAnnotationStep,
                                    ROIsAnnotation, ROIsAnnotationStep,
                                    update_annotation_session)
from slides_manager.models import Case, Slide


@pytest.fixture
def slide(case):
    return Slide.objects.create(case=case)


@pytest.fixture
def rois_annotation(reviewer, case):
    return ROIsAnnotation.objects.create(reviewer=reviewer, case=case)


@pytest.fixture
def reviewer():
    user = User.objects.create()
    return user


@pytest.fixture
def case():
    return Case.objects.create()


@pytest.fixture
def annotation_step(annotation_step_cls: Union[ROIsAnnotationStep, ClinicalAnnotationStep], rois_annotation, slide):
    if annotation_step_cls == ROIsAnnotationStep:
        return ROIsAnnotationStep.objects.create(label="test", rois_annotation=rois_annotation, slide=slide)
    else:
        ...


@pytest.mark.django_db
@pytest.mark.parametrize("annotation_step_cls", [ROIsAnnotationStep])
def test_session_create(annotation_step, annotation_step_cls):
    now = datetime.now()
    session = update_annotation_session(annotation_step, now)
    assert session.start_time == session.last_update == now
    assert not session.is_expired()

    time.sleep(1.1)
    now_2 = datetime.now()

    session_2 = update_annotation_session(annotation_step, now_2)
    assert session_2.id == session.id
    assert session.last_update < session_2.last_update

    AnnotationSession.EXPIRATION_TIME = 1
    assert session_2.is_expired()

    now_3 = datetime.now()
    session_3 = update_annotation_session(annotation_step, now_3)
    assert session_3.id != session_2.id

    AnnotationSession.EXPIRATION_TIME = 1000
    now_4 = datetime.now()
    session_4 = update_annotation_session(annotation_step, now_4)
    assert session_4.id == session_3.id
