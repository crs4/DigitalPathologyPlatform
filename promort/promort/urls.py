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
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns

from promort.views import IndexView
from authentication.views import LoginView, LogoutView, \
    GroupListView, GroupDetailsView, CheckUserView
from slides_manager.views import CaseList, CaseDetail, \
    SlideList, SlideDetail, SlideQualityControlDetail
from reviews_manager.views import ROIsAnnotationsList, ClinicalAnnotationsList, ROIsAnnotationsDetail, \
    ClinicalAnnotationsDetail, ROIsAnnotationDetail, ClinicalAnnotationDetail, ROIsAnnotationStepDetail, \
    ClinicalAnnotationStepDetail
from worklist_manager.views import UserWorkList, UserWorklistROIsAnnotation,\
    UserWorklistClinicalAnnotation, WorkListAdmin
from rois_manager.views import SliceList, SliceDetail, CoreList, \
    CoreDetail, FocusRegionList, FocusRegionDetail, ROIsTreeList
import utils.views as promort_utils

urlpatterns = [
    # authentication
    url(r'^api/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api/auth/check/$', CheckUserView.as_view()),

    # groups
    url(r'api/groups/$', GroupListView.as_view()),
    url(r'api/groups/(?P<group>rois_manager|clinical_manager|gold_standard)/$', GroupDetailsView.as_view()),

    # cases and slides
    url(r'^api/cases/$', CaseList.as_view()),
    url(r'^api/cases/(?P<pk>[\w\-.]+)/$', CaseDetail.as_view()),
    url(r'^api/slides/$', SlideList.as_view()),
    url(r'^api/slides/(?P<pk>[\w\-.]+)/$', SlideDetail.as_view()),

    # ROIs
    url(r'api/rois_annotation_steps/(?P<pk>[0-9]+)/rois_list/$', ROIsTreeList.as_view()),
    url(r'api/rois_annotation_steps/(?P<pk>[0-9]+)/slices/$', SliceList.as_view()),
    url(r'api/slices/(?P<pk>[0-9]+)/$', SliceDetail.as_view()),
    url(r'api/slices/(?P<pk>[0-9]+)/cores/$', CoreList.as_view()),
    url(r'api/cores/(?P<pk>[0-9]+)/$', CoreDetail.as_view()),
    url(r'api/cores/(?P<pk>[0-9]+)/focus_regions/$', FocusRegionList.as_view()),
    url(r'api/focus_regions/(?P<pk>[0-9]+)/$', FocusRegionDetail.as_view()),

    # ROIs annotations
    url(r'api/rois_annotations/$', ROIsAnnotationsList.as_view()),
    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/$', ROIsAnnotationsDetail.as_view()),
    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/$', ROIsAnnotationDetail.as_view()),
    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<slide>[\w\-.]+)/$',
        ROIsAnnotationStepDetail.as_view()),

    # quality control
    url(r'api/rois_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<slide>[\w\-.]+)/quality_control/$',
        SlideQualityControlDetail.as_view()),

    # clinical annotations
    url(r'api/clinical_annotations/$', ClinicalAnnotationsList.as_view()),
    url(r'api/clinical_annotations/(?P<case>[\w\-.]+)/$', ClinicalAnnotationsDetail.as_view()),
    url(r'api/clinical_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<rois_review>[0-9]+)/$',
        ClinicalAnnotationDetail.as_view()),
    url(r'api/clinical_annotations/(?P<case>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/(?P<rois_review>[0-9]+)/(?P<slide>[\w\-.]+)/$',
        ClinicalAnnotationStepDetail.as_view),

    # worklists
    url(r'api/worklist/$', UserWorkList.as_view()),
    url(r'api/worklist/(?P<case>[\w\-.]+)/$', UserWorklistROIsAnnotation.as_view()),
    url(r'api/worklist/(?P<case>[\w\-.]+)/(?P<rois_review>[0-9]+)/$', UserWorklistClinicalAnnotation.as_view()),
    url(r'api/worklist/admin/(?P<username>[\w\-.]+)/$', WorkListAdmin.as_view()),

    # utils
    url(r'api/utils/omeseadragon_base_urls/$', promort_utils.get_ome_seadragon_base_url),
    url(r'api/utils/slide_stainings/$', promort_utils.get_slide_stainings),
    url(r'api/utils/slide_not_adequacy_reasons/$', promort_utils.get_slide_qc_not_adequacy_reasons),
    url(r'api/utils/send_report/$', promort_utils.send_user_report),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # catch'em all
    url(r'^.*$', IndexView.as_view(), name='index'),
]

urlpatterns = format_suffix_patterns(urlpatterns)