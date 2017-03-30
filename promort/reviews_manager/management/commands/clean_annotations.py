from django.core.management.base import BaseCommand, CommandError

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep


class Command(BaseCommand):
    help = 'clean all annotations related to a specific ROIs Annotation step'

    def add_arguments(self, parser):
        parser.add_argument('--case', dest='case', type=str, required=True,
                            help='the label of the case of the slide')
        parser.add_argument('--slide', dest='slide', type=str, required=True,
                            help='the label of the slide associated to the ROIs annotation step')
        parser.add_argument('--reviewer', dest='reviewer', type=str, required=True,
                            help='the username of the reviewer associated to the ROIs annotation step')

    def handle(self, *args, **opts):
        try:
            rois_annotation = ROIsAnnotation.objects.get(case=opts['case'],
                                                         reviewer__username=opts['reviewer'])
            rois_annotation_step = rois_annotation.steps.get(slide=opts['slide'])
        except ROIsAnnotation.DoesNotExist:
            raise CommandError('There is no ROIs annotation for case %s assigned to reviewer %s'
                               % (opts['case'], opts['reviewer']))
        except ROIsAnnotationStep.DoesNotExist:
            raise CommandError('There is no ROIs annotation step for slide %s assigned to reviewer %s' %
                               (opts['slide'], opts['reviewer']))
        if rois_annotation_step.slide_quality_control.adequate_slide:
            clinical_annotation_steps = rois_annotation_step.clinical_annotation_steps.all()
            for clinical_step in clinical_annotation_steps:
                # get all slice annotations
                for slice_annotation in clinical_step.slice_annotations.all():
                    self.stdout.write('DELETE SliceAnnotation %r' % slice_annotation.id)
                    slice_annotation.delete()
                # get all core annotations
                for core_annotation in clinical_step.core_annotations.all():
                    self.stdout.write('DELETE CoreAnnotation %r' % core_annotation.id)
                    core_annotation.delete()
                # get all focus region annotations
                for focus_region_annotation in clinical_step.focus_region_annotations.all():
                    self.stdout.write('DELETE FocusRegionAnnotation %r' % focus_region_annotation.id)
                    focus_region_annotation.delete()
                # reset start and completion date for clinical annotation step
                self.stdout.write('ERASING START AND FINISH date for ClinicalAnnotationStep')
                clinical_step.start_date = None
                clinical_step.completion_date = None
                clinical_step.save()
                # also reopen clinical annotation (if needed)
                if clinical_step.clinical_annotation.is_completed():
                    self.stdout.write('REOPENING ClinicalAnnotation')
                    clinical_step.clinical_annotation.start_date = None
                    clinical_step.clinical_annotation.save()
            for slice in rois_annotation_step.slices.all():
                self.stdout.write('DELETE Slice %r (and related ROIs)' % slice.label)
                slice.delete()
            # reset start and completion fate for ROIs annotation step
            self.stdout.write('ERASING START AND FINISH date for ROIsAnnotationStep')
            rois_annotation_step.start_date = None
            rois_annotation_step.completion_date = None
            rois_annotation_step.save()
            # also reopen ROIs annotation (if needed)
            if rois_annotation.is_completed():
                self.stdout.write('REOPENING ROIsAnnotation')
                rois_annotation.completion_date = None
                rois_annotation.save()
        else:
            self.stdout.write('BAD QUALITY CONTROL for Slide, data won\'t be cleaned')
