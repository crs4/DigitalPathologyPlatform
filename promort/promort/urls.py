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
from authentication.views import LoginView, LogoutView
from slides_manager.views import CaseList, CaseDetail, \
    SlideList, SlideDetail, SlideQualityControlList


urlpatterns = [
    # authentication
    url(r'^api/auth/login/$', LoginView.as_view(), name='login'),
    url(r'^api/auth/logout/$', LogoutView.as_view(), name='logout'),

    # cases and slides
    url(r'^api/cases/$', CaseList.as_view()),
    url(r'^api/cases/(?P<pk>[\w\-.]+)/$', CaseDetail.as_view()),
    url(r'^api/slides/$', SlideList.as_view()),
    url(r'^api/slides/(?P<pk>[\w\-.]+)/$', SlideDetail.as_view()),
    # slide quality control
    url(r'api/slides/(?P<pk>[\w\-.]+)/quality_control/$',
        SlideQualityControlList.as_view()),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # catch'em all
    url(r'^.*$', IndexView.as_view(), name='index'),
]

urlpatterns = format_suffix_patterns(urlpatterns)