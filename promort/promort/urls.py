"""promort URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
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

from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns

from promort.views import IndexView
from authentication.views import LoginView, LogoutView, \
    GroupListView, GroupDetailsView, CheckUserView
from slides_manager.views import LaboratoryList, LaboratoryDetail, LaboratoryCaseLink, \
    CaseList, CaseDetail, SlideList, SlideDetail, SlideEvaluationDetail, SlidesSetList, SlidesSetDetail
import reviews_manager.views as rmv
from worklist_manager.views import UserWorkList, UserWorklistROIsAnnotation,\
    UserWorklistClinicalAnnotation, WorkListAdmin
from rois_manager.views import SliceList, SliceDetail, CoreList, \
    CoreDetail, FocusRegionList, FocusRegionDetail, ROIsTreeList
from clinical_annotations_manager.views import AnnotatedROIsTreeList, ClinicalAnnotationStepAnnotationsList,\
    SliceAnnotationList, SliceAnnotationDetail, CoreAnnotationList, CoreAnnotationDetail, \
    FocusRegionAnnotationList, FocusRegionAnnotationDetail
import odin.views as od
import utils.views as promort_utils

urlpatterns = [
    # authentication
    url(r'^api/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api/auth/check/$', CheckUserView.as_view()),

    # groups
    url(r'api/groups/$', GroupListView.as_view()),
    url(r'api/groups/(?P<group>rois_manager|clinical_manager|gold_standard)/$', GroupDetailsView.as_view()),

    # laboratories, cases and slides
    url(r'^api/laboratories/$', LaboratoryList.as_view()),
    url(r'^api/laboratories/(?P<pk>[\w\-.]+)/$', LaboratoryDetail.as_view()),
    url(r'^api/laboratories/(?P<laboratory>[\w\-.]+)/(?P<case>[\w\-.]+)/$', LaboratoryCaseLink.as_view()),
    url(r'^api/cases/$', CaseList.as_view()),
    url(r'^api/cases/(?P<pk>[\w\-.]+)/$', CaseDetail.as_view()),
    url(r'^api/slides/$', SlideList.as_view()),
    url(r'^api/slides/(?P<pk>[\w\-.]+)/$', SlideDetail.as_view()),
    url(r'^api/slides_set/$', SlidesSetList.as_view()),
    url(r'^api/slides_set/(?P<pk>[\w\-.]+)/$', SlidesSetDetail.as_view()),

    # ROIs annotation steps details
    url(r'api/rois_annotation_steps/(?P<label>[A-Fa-f0-9\-.]+)/clinical_annotation_steps/$',
        rmv.ClinicalAnnotationStepsList.as_view()),

    # ROIs
    url(r'api/rois_annotation_steps/(?P<label>[A-Fa-f0-9\-.]+)/rois_list/$', ROIsTreeList.as_view()),
    url(r'api/rois_annotation_steps/(?P<label>[A-Fa-f0-9\-.]+)/slices/$', SliceList.as_view()),
    url(r'api/slices/(?P<pk>[0-9]+)/$', SliceDetail.as_view()),
    url(r'api/slices/(?P<pk>[0-9]+)/cores/$', CoreList.as_view()),
    url(r'api/cores/(?P<pk>[0-9]+)/$', CoreDetail.as_view()),
    url(r'api/cores/(?P<pk>[0-9]+)/focus_regions/$', FocusRegionList.as_view()),
    url(r'api/focus_regions/(?P<pk>[0-9]+)/$', FocusRegionDetail.as_view()),

    # clinical annotations data
    url(r'api/rois_annotation_steps/(?P<rois_annotation_step>[A-Fa-f0-9\-.]+)/rois_list/(?P<clinical_annotation_step>[A-Fa-f0-9\-.]+)/$',
        AnnotatedROIsTreeList.as_view()),
    url('api/clinical_annotation_steps/(?P<clinical_annotation_step>[A-Fa-f0-9\-.]+)/annotations_list/',
        ClinicalAnnotationStepAnnotationsList.as_view()),
    url(r'api/slices/(?P<slice_id>[0-9]+)/clinical_annotations/$', SliceAnnotationList.as_view()),
    url(r'api/slices/(?P<slice_id>[0-9]+)/clinical_annotations/(?P<label>[A-Fa-f0-9\-.]+)/$',
        SliceAnnotationDetail.as_view()),
    url(r'api/cores/(?P<core_id>[0-9]+)/clinical_annotations/$', CoreAnnotationList.as_view()),
    url(r'api/cores/(?P<core_id>[0-9]+)/clinical_annotations/(?P<label>[A-Fa-f0-9\-.]+)/$',
        CoreAnnotationDetail.as_view()),
    url(r'api/focus_regions/(?P<focus_region_id>[0-9]+)/clinical_annotations/$',
        FocusRegionAnnotationList.as_view()),
    url(r'api/focus_regions/(?P<focus_region_id>[0-9]+)/clinical_annotations/(?P<label>[A-Fa-f0-9\-.]+)/$',
        FocusRegionAnnotationDetail.as_view()),

    # ROIs annotations
    url(r'api/rois_annotations/$', rmv.ROIsAnnotationsList.as_view()),
    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/$', rmv.ROIsAnnotationsDetail.as_view()),
    url(r'api/rois_annotations/annotations/(?P<label>[A-Fa-f0-9]+)/$', rmv.ROIsAnnotationDetail.as_view()),
    url(r'api/rois_annotations/steps/(?P<label>[A-Fa-f0-9\-.]+)/$', rmv.ROIsAnnotationStepDetail.as_view()),
    url(r'api/rois_annotations/steps/(?P<label>[A-Fa-f0-9\-.]+)/reset/$', rmv.ROIsAnnotationStepReopen.as_view()),

    # quality control
    url(r'api/rois_annotations/steps/(?P<label>[A-Fa-f0-9\-.]+)/slide_evaluation/$',
        SlideEvaluationDetail.as_view()),

    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/$', rmv.ROIsAnnotationCreation.as_view()),
    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<slide>[\w\-.]+)/$',
        rmv.ROIsAnnotationStepCreation.as_view()),

    # clinical annotations
    url(r'api/clinical_annotations/$', rmv.ClinicalAnnotationsList.as_view()),
    url(r'api/clinical_annotations/(?P<case>[\w\-.]+)/$', rmv.ClinicalAnnotationsDetail.as_view()),
    url(r'api/clinical_annotations/annotations/(?P<label>[A-Fa-f0-9]+)/$', rmv.ClinicalAnnotationDetail.as_view()),
    url(r'api/clinical_annotations/steps/(?P<label>[A-Fa-f0-9\-.]+)/$', rmv.ClinicalAnnotationStepDetail.as_view()),

    url(r'api/clinical_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<rois_review>[0-9]+)/$',
        rmv.ClinicalAnnotationCreation.as_view()),
    url(r'api/clinical_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<rois_review>[0-9]+)/(?P<slide>[\w\-.]+)/$',
        rmv.ClinicalAnnotationStepCreation.as_view()),

    # worklists
    url(r'api/worklist/$', UserWorkList.as_view()),
    url(r'api/worklist/rois_annotations/(?P<label>[A-Fa-f0-9]+)/$', UserWorklistROIsAnnotation.as_view()),
    url(r'api/worklist/clinical_annotations/(?P<label>[A-Fa-f0-9]+)/$', UserWorklistClinicalAnnotation.as_view()),
    url(r'api/worklist/admin/(?P<username>[\w\-.]+)/$', WorkListAdmin.as_view()),

    # utils
    url(r'api/utils/omeseadragon_base_urls/$', promort_utils.get_ome_seadragon_base_url),
    url(r'api/utils/slide_stainings/$', promort_utils.get_slide_stainings),
    url(r'api/utils/slide_not_adequacy_reasons/$', promort_utils.get_slide_qc_not_adequacy_reasons),
    url(r'api/utils/clinical_step_rejection_reasons/$', promort_utils.get_clinical_step_rejection_reasons),
    url(r'api/utils/send_report/$', promort_utils.send_user_report),

    # ===== ODIN BACKEND ======
    #utils
    url(r'api/odin/check_permissions/$', od.CheckAccessPrivileges.as_view()),

    # ROIs extraction tool
    url(r'api/odin/rois/(?P<case>[\w\-.]+)/$', od.GetCaseDetails.as_view()),
    url(r'api/odin/rois/(?P<slide>[\w\-.]+)/slices/$', od.GetSlicesDetails.as_view()),
    url(r'api/odin/rois/(?P<slide>[\w\-.]+)/slices/(?P<pk>[0-9]+)/$', od.GetSliceDetails.as_view()),
    url(r'api/odin/rois/(?P<slide>[\w\-.]+)/cores/$', od.GetCoresDetails.as_view()),
    url(r'api/odin/rois/(?P<slide>[\w\-.]+)/cores/(?P<pk>[0-9]+)/$', od.GetCoreDetails.as_view()),
    url(r'api/odin/rois/(?P<slide>[\w\-.]+)/focus_regions/$', od.GetFocusRegionsDetails.as_view()),
    url(r'api/odin/rois/(?P<slide>[\w\-.]+)/focus_regions/(?P<pk>[0-9]+)/$', od.GetFocusRegionDetails.as_view()),
    url(r'api/odin/rois/(?P<case>[\w\-.]+)/(?P<slide>[\w\-.]+)/$', od.GetSlideDetails.as_view()),
    url(r'api/odin/rois/(?P<case>[\w\-.]+)/(?P<slide>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/$',
        od.GetReviewerDetails.as_view()),
    url(r'api/odin/rois/(?P<case>[\w\-.]+)/(?P<slide>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/'
        r'(?P<roi_type>slice|core|focus_region)/$', od.GetDetailsByROIType.as_view()),
    url(r'api/odin/rois/(?P<case>[\w\-.]+)/(?P<slide>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/'
        r'(?P<roi_type>slice|core|focus_region)/(?P<roi_label>[\w]+)/$', od.GetROIDetails.as_view()),

    # clinical reviews report tools
    url(r'api/odin/reviews/(?P<case>[\w\-.]+)/score/$', od.CaseReviewResults.as_view()),
    url(r'api/odin/reviews/(?P<case>[\w\-.]+)/score/details/$', od.CaseReviewResultsDetails.as_view()),

    # reviewers activity report
    url(r'api/odin/reviewers_report/$', od.ReviewersDetails.as_view()),
    url(r'api/odin/reviewers_report/send/$', od.ReviewersDetailsReport.as_view()),
    url(r'api/odin/reviews_activity_report/send/$', od.ReviewsActivityReport.as_view()),

    # quality control tools
    url(r'api/odin/quality_control/bad_slides/$', od.BadSlideDetails.as_view()),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # catch'em all
    url(r'^.*$', IndexView.as_view(), name='index'),
]

urlpatterns = format_suffix_patterns(urlpatterns)