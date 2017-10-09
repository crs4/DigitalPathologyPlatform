from django.contrib.auth.models import Group

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from odin.permissions import CanEnterGodMode

from reviews_manager.models import ROIsAnnotation, ClinicalAnnotation

from promort.settings import DEFAULT_GROUPS

from collections import Counter

import logging
logger = logging.getLogger('promort')


class ReviewersDetails(APIView):
    permission_classes = (CanEnterGodMode,)

    def _get_infos(self, annotations_list):
        infos = Counter()
        slides = Counter()
        infos['assigned_reviews'] = len(annotations_list)
        for annotation in annotations_list:
            if annotation.is_completed():
                infos['completed_reviews'] += 1
            else:
                infos['not_completed_reviews'] += 1
            for step in annotation.steps.all():
                if step.is_completed():
                    slides['completed'] += 1
                else:
                    slides['not_completed'] += 1
        infos['slides_details'] = slides
        return infos

    def _get_reviews_status(self, reviewer):
        roi_annotations = ROIsAnnotation.objects.filter(reviewer=reviewer)
        clinical_annotations = ClinicalAnnotation.objects.filter(reviewer=reviewer)
        return {
            'roi_annotations': self._get_infos(roi_annotations),
            'clinical_annotations': self._get_infos(clinical_annotations)
        }

    def _get_reviewers_by_group(self, group_name):
        logger.info('Loading users for group %s', group_name)
        group = Group.objects.get(name=group_name)
        return group.user_set.all()

    def _get_reviewers_list(self):
        reviewers = set()
        for glabel in ['rois_manager', 'clinical_manager', 'gold_standard']:
            reviewers.update(self._get_reviewers_by_group(DEFAULT_GROUPS[glabel]['name']))
        return reviewers

    def _get_reviewers_details(self):
        details = dict()
        reviewers = self._get_reviewers_list()
        for rev in reviewers:
            details[rev.username] = self._get_reviews_status(rev)
        return details

    def get(self, request, format=None):
        infos_map = self._get_reviewers_details()
        return Response(infos_map, status=status.HTTP_200_OK)
