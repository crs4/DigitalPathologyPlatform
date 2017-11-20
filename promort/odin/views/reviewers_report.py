from django.contrib.auth.models import Group, User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from odin.permissions import CanEnterGodMode

from reviews_manager.models import ROIsAnnotation, ClinicalAnnotation

from promort.settings import DEFAULT_GROUPS, EMAIL_HOST_USER, REPORT_RECIPIENTS

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


class ReviewersDetailsReport(ReviewersDetails):

    def _get_user_details(self, username):
        user_obj = User.objects.get(username=username)
        return {
            'name': user_obj.first_name,
            'surname': user_obj.last_name,
            'email': user_obj.email
        }


    def _get_template_context(self, user_details, reviews_details):
        tmpl_ctx = {
            'assigned_rois_reviews': reviews_details['roi_annotations']['assigned_reviews'],
            'assigned_clinical_reviews': reviews_details['clinical_annotations']['assigned_reviews']
        }
        if tmpl_ctx['assigned_rois_reviews'] > 0:
            tmpl_ctx.update({
                'completed_rois_reviews': reviews_details['roi_annotations']['completed_reviews'],
                'not_completed_rois_reviews': reviews_details['roi_annotations']['not_completed_reviews'],
                'rois_annotated_slides': reviews_details['roi_annotations']['slides_details']['completed'],
                'rois_not_annotated_slides': reviews_details['roi_annotations']['slides_details']['not_completed']
            })
        if tmpl_ctx['assigned_clinical_reviews'] > 0:
            tmpl_ctx.update({
                'completed_clinical_reviews': reviews_details['clinical_annotations']['completed_reviews'],
                'not_completed_clinical_reviews': reviews_details['clinical_annotations']['not_completed_reviews'],
                'clinical_annotated_slides': reviews_details['clinical_annotations']['slides_details']['completed'],
                'clinical_not_annotated_slides':
                    reviews_details['clinical_annotations']['slides_details']['not_completed']
            })
        tmpl_ctx.update(user_details)
        return tmpl_ctx

    def _send_mail(self, reviewer, reviews_details, text_mail_template, html_mail_template):
        usr_details = self._get_user_details(reviewer)
        destination_mail = usr_details.pop('email')
        template_ctx = self._get_template_context(usr_details, reviews_details)

        subject = '[ProMort] Reviewer activity report'
        from_email = EMAIL_HOST_USER
        bcc_mails = REPORT_RECIPIENTS

        msg = EmailMultiAlternatives(subject=subject, body=text_mail_template.render(template_ctx),
                                     from_email=from_email, to=[destination_mail], bcc=bcc_mails)
        msg.attach_alternative(html_mail_template.render(template_ctx), 'text/html')
        logger.info('Sending mail to %s', destination_mail)
        msg.send()

    def get(self, request, format=None):
        text_template = get_template('reviewer_report.txt')
        html_template = get_template('reviewer_report.html')

        send_mail_status = dict()

        reviews_map = self._get_reviewers_details()
        for reviewer, annotations_details in reviews_map.iteritems():
            try:
                self._send_mail(reviewer, annotations_details, text_template, html_template)
                send_mail_status[reviewer] = True
            except:
                send_mail_status[reviewer] = False

        return Response(send_mail_status, status=status.HTTP_200_OK)