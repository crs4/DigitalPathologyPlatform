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
from reviews_manager.views import ReviewsList, ReviewsDetail,\
    ReviewDetail, ReviewStepDetail
from worklist_manager.views import UserWorkList, UserWorkListReview,\
    WorkListAdmin
import utils.views as promort_utils

urlpatterns = [
    # authentication
    url(r'^api/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^api/auth/check/$', CheckUserView.as_view()),

    # groups
    url(r'api/groups/$', GroupListView.as_view()),
    url(r'api/groups/(?P<group>reviewer_1|reviewer_2|reviewer_3)/$', GroupDetailsView.as_view()),

    # cases and slides
    url(r'^api/cases/$', CaseList.as_view()),
    url(r'^api/cases/(?P<pk>[\w\-.]+)/$', CaseDetail.as_view()),
    url(r'^api/slides/$', SlideList.as_view()),
    url(r'^api/slides/(?P<pk>[\w\-.]+)/$', SlideDetail.as_view()),

    # slide quality control
    url(r'api/slides/(?P<slide>[\w\-.]+)/quality_control/$',
        SlideQualityControlDetail.as_view()),

    # reviews and review steps
    url(r'api/reviews/$', ReviewsList.as_view()),
    url(r'api/reviews/(?P<case>[\w\-.]+)/$', ReviewsDetail.as_view()),
    url(r'api/reviews/(?P<case>[\w\-.]+)/(?P<review_type>review_1|review_2|review_3)/$',
        ReviewDetail.as_view()),
    url(r'api/reviews/(?P<case>[\w\-.]+)/(?P<review_type>review_1|review_2|review_3)/(?P<slide>[\w\-.]+)/$',
        ReviewStepDetail.as_view()),

    # worklists
    url(r'api/worklist/$', UserWorkList.as_view()),
    url(r'api/worklist/(?P<case>[\w\-.]+)/$', UserWorkListReview.as_view()),
    url(r'api/worklist/admin/(?P<username>[\w.]+)/$', WorkListAdmin.as_view()),

    # utils
    url(r'api/utils/omeseadragon_base_urls/$', promort_utils.get_ome_seadragon_base_url),
    url(r'api/utils/slide_not_adequacy_reasons/$', promort_utils.get_slide_qc_not_adequacy_reasons),
    url(r'api/utils/send_report/$', promort_utils.send_user_report),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # catch'em all
    url(r'^.*$', IndexView.as_view(), name='index'),
]

urlpatterns = format_suffix_patterns(urlpatterns)