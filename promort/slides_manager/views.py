from view_templates.views import GenericDetailView, GenericListView
from rest_framework import permissions


from slides_manager.models import Case, Slide
from slides_manager.serializers import CaseSerializer, CaseDetailedSerializer,\
    SlideSerializer


class CaseList(GenericListView):
    model = Case
    model_serializer = CaseSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CaseDetail(GenericDetailView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Case
    model_serializer = CaseDetailedSerializer


class SlideList(GenericListView):
    model = Slide
    model_serializer = SlideSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SlideDetail(GenericDetailView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Slide
    model_serializer = SlideSerializer
