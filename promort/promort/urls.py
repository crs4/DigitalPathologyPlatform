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

from django.contrib import admin
from django.urls import path, re_path, register_converter

from rest_framework.urlpatterns import format_suffix_patterns

from .views import IndexView
from authentication.views import LoginView, LogoutView, \
    GroupListView, GroupDetailsView, CheckUserView, ChangePasswordView
from slides_manager.views import LaboratoryList, LaboratoryDetail, LaboratoryCaseLink, \
    CaseList, CaseDetail, SlideList, SlideDetail, SlideEvaluationDetail, SlidesSetList, SlidesSetDetail
import questionnaires_manager.views as qmv
import reviews_manager.views as rmv
from worklist_manager.views import UserWorkList, UserWorklistROIsAnnotation, \
    UserWorklistClinicalAnnotation, WorkListAdmin
from rois_manager.views import SlideROIsList, SliceList, SliceDetail, CoreList, \
    CoreDetail, FocusRegionList, FocusRegionDetail, ROIsTreeList
from clinical_annotations_manager.views import AnnotatedROIsTreeList, ClinicalAnnotationStepAnnotationsList, \
    SliceAnnotationList, SliceAnnotationDetail, CoreAnnotationList, CoreAnnotationDetail, \
    FocusRegionAnnotationList, FocusRegionAnnotationDetail
import predictions_manager.views as pmv
import shared_datasets_manager.views as shdv
import odin.views as od
import utils.views as promort_utils


class NumericString:
    regex = r'[0-9]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class RandomCaseLabel:
    regex = r'[A-Fa-f0-9]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
   

class RandomSlideLabel:
    regex = r'[A-Fa-f0-9]+\-[A-Za-z0-9]{1,2}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(NumericString, 'num')
register_converter(RandomCaseLabel, 'rclabel')
register_converter(RandomSlideLabel, 'rslabel')

urlpatterns = [
    # authentication
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/check/', CheckUserView.as_view()),
    path('api/auth/change_password/',
         ChangePasswordView.as_view(),
         name='change_password'),

    # groups
    path('api/groups/', GroupListView.as_view()),
    re_path(
        'api/groups/(?P<group>rois_manager|clinical_manager|gold_standard)/',
        GroupDetailsView.as_view()),

    # laboratories, cases and slides
    path('api/laboratories/', LaboratoryList.as_view()),
    path('api/laboratories/<slug:pk>/', LaboratoryDetail.as_view()),
    path('api/laboratories/<slug:laboratory>/<slug:case>/',
         LaboratoryCaseLink.as_view()),
    path('api/cases/', CaseList.as_view()),
    path('api/cases/<slug:pk>/', CaseDetail.as_view()),
    path('api/slides/', SlideList.as_view()),
    path('api/slides/<slug:pk>/', SlideDetail.as_view()),
    path('api/slides_set/', SlidesSetList.as_view()),
    path('api/slides_set/<slug:pk>/', SlidesSetDetail.as_view()),

    # slides questionnaire
    path('api/questions_sets/', qmv.QuestionsSetList.as_view()),
    path('api/questions_sets/<slug:pk>/', qmv.QuestionsSetDetail.as_view()),
    path('api/questionnaires/', qmv.QuestionnaireList.as_view()),
    path('api/questionnaires/<slug:pk>/', qmv.QuestionnaireDetail.as_view()),
    path('api/questionnaires/<slug:quest_pk>/<num:step_index>/',
         qmv.QuestionnaireStepDetail.as_view()),

    # slides questionnaire worklist and answers
    path('api/questionnaire_requests/<slug:label>/',
         qmv.QuestionnaireRequestDetail.as_view()),
    path('api/questionnaire_requests/<slug:label>/status/',
         qmv.QuestionnaireRequestStatus.as_view()),
    path('api/questionnaire_requests/<slug:label>/answers/',
         qmv.QuestionnaireRequestAnswers.as_view()),
    re_path(
        r'api/questionnaire_requests/(?P<label>[\w\-.]+)/(?P<panel>panel_a|panel_b)/',
        qmv.QuestionnaireRequestPanelDetail.as_view()),
    re_path(
        r'api/questionnaire_requests/(?P<label>[\w\-.]+)/(?P<panel>panel_a|panel_b)/answers/',
        qmv.QuestionnairePanelAnswersDetail.as_view()),

    # ROIs annotation steps details
    path(
        'api/rois_annotation_steps/<rslabel:label>/clinical_annotation_steps/',
        rmv.ClinicalAnnotationStepsList.as_view()),

    # ROIs
    path('api/slides/<slug:pk>/rois/', SlideROIsList.as_view()),
    path('api/rois_annotation_steps/<rslabel:label>/rois_list/',
         ROIsTreeList.as_view()),
    path('api/rois_annotation_steps/<rslabel:label>/slices/',
         SliceList.as_view()),
    path('api/slices/<num:pk>/cores/', CoreList.as_view()),
    path('api/slices/<num:pk>/', SliceDetail.as_view()),
    path('api/cores/<num:pk>/focus_regions/', FocusRegionList.as_view()),
    path('api/cores/<num:pk>/', CoreDetail.as_view()),
    path('api/focus_regions/<num:pk>/', FocusRegionDetail.as_view()),

    # clinical annotations data
    path(
        'api/rois_annotation_steps/<rslabel:rois_annotation_step>/rois_list/<rslabel:clinical_annotation_step>/',
        AnnotatedROIsTreeList.as_view()),
    path(
        'api/clinical_annotation_steps/<rslabel:clinical_annotation_step>/annotations_list/',
        ClinicalAnnotationStepAnnotationsList.as_view()),
    path('api/slices/<num:slice_id>/clinical_annotations/',
         SliceAnnotationList.as_view()),
    path('api/slices/<num:slice_id>/clinical_annotations/<rslabel:label>/',
         SliceAnnotationDetail.as_view()),
    path('api/cores/<num:core_id>/clinical_annotations/',
         CoreAnnotationList.as_view()),
    path('api/cores/<num:core_id>/clinical_annotations/<rslabel:label>/',
         CoreAnnotationDetail.as_view()),
    path('api/focus_regions/<num:focus_region_id>/clinical_annotations/',
         FocusRegionAnnotationList.as_view()),
    path(
        'api/focus_regions/<num:focus_region_id>/clinical_annotations/<rslabel:label>/',
        FocusRegionAnnotationDetail.as_view()),

    # ROIs annotations
    path('api/rois_annotations/', rmv.ROIsAnnotationsList.as_view()),
    path('api/rois_annotations/annotations/<rclabel:label>/',
         rmv.ROIsAnnotationDetail.as_view()),
    path('api/rois_annotations/steps/<rslabel:label>/reset/',
         rmv.ROIsAnnotationStepReopen.as_view()),
    path('api/rois_annotations/steps/<rslabel:label>/',
         rmv.ROIsAnnotationStepDetail.as_view()),
    path('api/rois_annotations/<slug:case>/',
         rmv.ROIsAnnotationsDetail.as_view()),

    # quality control
    path('api/rois_annotations/steps/<rslabel:label>/slide_evaluation/',
         SlideEvaluationDetail.as_view()),
    path('api/rois_annotations/<slug:case>/<slug:reviewer>/',
         rmv.ROIsAnnotationCreation.as_view()),
    path('api/rois_annotations/<slug:case>/<slug:reviewer>/<slug:slide>/',
         rmv.ROIsAnnotationStepCreation.as_view()),

    # clinical annotations
    path('api/clinical_annotations/', rmv.ClinicalAnnotationsList.as_view()),
    path('api/clinical_annotations/<slug:case>/',
         rmv.ClinicalAnnotationsDetail.as_view()),
    path('api/clinical_annotations/annotations/<rclabel:label>/',
         rmv.ClinicalAnnotationDetail.as_view()),
    path('api/clinical_annotations/steps/<rslabel:label>/',
         rmv.ClinicalAnnotationStepDetail.as_view()),
    path(
        'api/clinical_annotations/<slug:case>/<slug:reviewer>/<num:rois_review>/',
        rmv.ClinicalAnnotationCreation.as_view()),
    path(
        'api/clinical_annotations/<slug:case>/<slug:reviewer>/<num:rois_review>/<slug:slide>/',
        rmv.ClinicalAnnotationStepCreation.as_view()),
    
    # predictions reviews
    path('api/prediction_reviews/', rmv.PredictionReviewsList.as_view()),
    path('api/prediction_reviews/<slug:slide>/', rmv.PredictionReviewsDetail.as_view()),
    path('api/prediction_review/<rclabel:label>/', rmv.PredictionReviewDetail.as_view()),
    path('api/prediction_review/<rslabel:label>/prediction/', rmv.PredictionByReviewDetail.as_view()),

    # predictions
    path('api/predictions/', pmv.PredictionList.as_view()),
    path('api/predictions/<slug:pk>/', pmv.PredictionDetail.as_view()),
    path('api/predictions/<slug:pk>/require_review/', pmv.PredictionRequireReview.as_view()),

    #  tissue fragments
    path('api/tissue_fragments_collections/',
         pmv.TissueFragmentsCollectionList.as_view()),  # GET, POST
    path('api/tissue_fragments_collections/<slug:pk>/',
         pmv.TissueFragmentsCollectionDetail.as_view()
         ),  # GET, DELETE, PUT (se usi GenericDetailView)
    path('api/tissue_fragments_collections/<slug:coll_id>/fragments/',
         pmv.TissueFragmentList.as_view()),  # POST
    path('api/tissue_fragments_collections/<slug:coll_id>/fragments/<slug:pk>/',
         pmv.TissueFragmentsDetail.as_view()),  # DELETE

    # worklists
    path('api/worklist/', UserWorkList.as_view()),
    path('api/worklist/rois_annotations/<rclabel:label>/',
         UserWorklistROIsAnnotation.as_view()),
    path('api/worklist/clinical_annotations/<rclabel:label>/',
         UserWorklistClinicalAnnotation.as_view()),
    path('api/worklist/admin/<slug:username>/', WorkListAdmin.as_view()),

    # utils
    path('api/utils/omeseadragon_base_urls/',
         promort_utils.get_ome_seadragon_base_url),
    path('api/utils/slide_stainings/', promort_utils.get_slide_stainings),
    path('api/utils/slide_not_adequacy_reasons/',
         promort_utils.get_slide_qc_not_adequacy_reasons),
    path('api/utils/clinical_step_rejection_reasons/',
         promort_utils.get_clinical_step_rejection_reasons),
    path('api/utils/gleason_element_types/',
         promort_utils.get_gleason_element_types),
    path('api/utils/send_report/', promort_utils.send_user_report),

    # ===== SHARED DATASETS =====
    path('api/shared_datasets/', shdv.SharedDatasetList.as_view()),
    path('api/shared_datasets/<slug:pk>/', shdv.SharedDatasetDetail.as_view()),
    path('api/shared_datasets/<slug:dataset>/<slug:index>/',
         shdv.SharedDatasetItemDetail.as_view()),

    # ===== ODIN BACKEND ======
    # utils
    path('api/odin/check_permissions/', od.CheckAccessPrivileges.as_view()),

    # ROIs extraction tool
    path('api/odin/rois/<slug:case>/', od.GetCaseDetails.as_view()),
    path('api/odin/rois/<slug:slide>/slices/', od.GetSlicesDetails.as_view()),
    path('api/odin/rois/<slug:slide>/slices/<num:pk>/',
         od.GetSliceDetails.as_view()),
    path('api/odin/rois/<slug:slide>/cores/', od.GetCoresDetails.as_view()),
    path('api/odin/rois/<slug:slide>/cores/<num:pk>/',
         od.GetCoreDetails.as_view()),
    path('api/odin/rois/<slug:slide>/focus_regions/',
         od.GetFocusRegionsDetails.as_view()),
    path('api/odin/rois/<slug:slide>/focus_regions/<num:pk>/',
         od.GetFocusRegionDetails.as_view()),
    path('api/odin/rois/<slug:case>/<slug:slide>/',
         od.GetSlideDetails.as_view()),
    path('api/odin/rois/<slug:case>/<slug:slide>/<slug:reviewer>/',
         od.GetReviewerDetails.as_view()),
    re_path(
        r'api/odin/rois/(?P<case>[\w\-.]+)/(?P<slide>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/'
        r'(?P<roi_type>slice|core|focus_region)/',
        od.GetDetailsByROIType.as_view()),
    re_path(
        r'api/odin/rois/(?P<case>[\w\-.]+)/(?P<slide>[\w\-.]+)/(?P<reviewer>[\w\-.]+)/'
        r'(?P<roi_type>slice|core|focus_region)/(?P<roi_label>[\w]+)/',
        od.GetROIDetails.as_view()),

    # clinical reviews report tools
    path('api/odin/reviews/<slug:case>/score/',
         od.CaseReviewResults.as_view()),
    path('api/odin/reviews/<slug:case>/score/details/',
         od.CaseReviewResultsDetails.as_view()),

    # reviewers activity report
    path('api/odin/reviewers_report/', od.ReviewersDetails.as_view()),
    path('api/odin/reviewers_report/send/',
         od.ReviewersDetailsReport.as_view()),
    path('api/odin/reviews_activity_report/send/',
         od.ReviewsActivityReport.as_view()),

    # quality control tools
    path('api/odin/quality_control/bad_slides/', od.BadSlideDetails.as_view()),

    # Django admin
    path('admin/', admin.site.urls),

    # catch'em all
    re_path(r'.*', IndexView.as_view(), name='index'),
    # path('', IndexView.as_view(), name='index'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
