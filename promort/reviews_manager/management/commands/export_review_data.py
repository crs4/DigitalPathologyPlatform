from django.core.management.base import BaseCommand, CommandError

import os
import datetime
import logging
from csv import DictWriter

from rois_manager.models import Slice, Core, FocusRegion
from slides_manager.models import SlideEvaluation
from clinical_annotations_manager.models import GleasonElement


logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'export annotations data to CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--dest_folder', dest='out_folder', type=str, required=True,
                            help='the destination folder for CSV output files')

    def _create_export_dir(self, container_folder):
        export_dir = os.path.join(container_folder, '{:%Y_%m_%d_%H:%M:%S}'.format(datetime.datetime.now()))
        try:
            os.mkdir(export_dir)
            return export_dir
        except OSError:
            raise CommandError('Can\'t create output folder %s' % export_dir)

    def _export_bad_quality_slides(self, output_folder):
        logger.info('Loading quality control data')
        bad_qc = SlideEvaluation.objects.filter(adequate_slide=False)
        logger.debug('Bad Quality control found: %d', len(bad_qc))
        logger.info('Saving bad quality control data')
        with open(os.path.join(output_folder, 'bad_quality_control.csv'), 'w') as ofile:
            writer = DictWriter(ofile, ['case', 'slide', 'not_adequacy_reason', 'notes'], delimiter=';')
            writer.writeheader()
            for bqc in bad_qc:
                writer.writerow({
                    'case': bqc.slide.case.id,
                    'slide': bqc.slide.id,
                    'not_adequacy_reason': bqc.not_adequacy_reason,
                    'notes': bqc.notes
                })
        logger.info('Done with quality control data')

    def _export_slices_info(self, output_folder):
        logger.info('Loading slice data')
        slices = Slice.objects.all()
        logger.info('Loaded %d slices', len(slices))
        logger.info('Saving slice data')
        header = ['case', 'slide', 'label', 'rois_reviewer', 'clinical_reviewer', 'total_cores', 'positive_cores',
                  'high_grade_pin', 'pah', 'chronic_inflammation', 'acute_inflammation', 'periglandular_inflammation',
                  'intraglandular_inflammation', 'stromal_inflammation']
        with open(os.path.join(output_folder, 'slices.csv'), 'w') as ofile:
            writer = DictWriter(ofile, header, delimiter=';')
            writer.writeheader()
            for slice in slices:
                annotations = slice.clinical_annotations.all()
                if len(annotations) > 0:
                    for annotation in annotations:
                        writer.writerow({
                            'case': slice.slide.case.id,
                            'slide': slice.slide.id,
                            'label': slice.label,
                            'rois_reviewer': slice.annotation_step.rois_annotation.reviewer.username,
                            'clinical_reviewer': annotation.author.username,
                            'total_cores': slice.total_cores,
                            'positive_cores': slice.get_positive_cores_count(),
                            'high_grade_pin': annotation.high_grade_pin,
                            'pah': annotation.pah,
                            'chronic_inflammation': annotation.chronic_inflammation,
                            'acute_inflammation': annotation.acute_inflammation,
                            'periglandular_inflammation': annotation.periglandular_inflammation,
                            'intraglandular_inflammation': annotation.intraglandular_inflammation,
                            'stromal_inflammation': annotation.stromal_inflammation
                        })
                else:
                    writer.writerow({
                        'case': slice.slide.case.id,
                        'slide': slice.slide.id,
                        'label': slice.label,
                        'rois_reviewer': slice.annotation_step.rois_annotation.reviewer.username,
                        'total_cores': slice.total_cores,
                        'positive_cores': slice.get_positive_cores_count()
                    })
        logger.info('Done with slice data')

    def _export_cores_info(self, output_folder):
        logger.info('Loading core data')
        cores = Core.objects.all()
        logger.info('Loaded %d cores', len(cores))
        logger.info('Saving core data')
        header = ['case', 'slide', 'slice', 'label', 'rois_reviewer', 'clinical_reviewer', 'length', 'area', 'positive',
                  'tumor_length', 'normal_tissue_percentage', 'primary_gleason', 'secondary_gleason', 'gleason_group',
                  'gleason_4_percentage']
        with open(os.path.join(output_folder, 'cores.csv'), 'w') as ofile:
            writer = DictWriter(ofile, header, delimiter=';')
            writer.writeheader()
            for core in cores:
                annotations = core.clinical_annotations.all()
                if len(annotations) > 0:
                    for annotation in annotations:
                        writer.writerow({
                            'case': core.slice.slide.case.id,
                            'slide': core.slice.slide.id,
                            'slice': core.slice.label,
                            'label': core.label,
                            'length': core.length,
                            'area': core.area,
                            'positive': core.is_positive(),
                            'tumor_length': core.tumor_length,
                            'normal_tissue_percentage': core.get_normal_tissue_percentage(),
                            'rois_reviewer': core.slice.annotation_step.rois_annotation.reviewer.username,
                            'clinical_reviewer': annotation.author.username,
                            'primary_gleason': annotation.primary_gleason,
                            'secondary_gleason': annotation.secondary_gleason,
                            'gleason_group': annotation.gleason_group,
                            'gleason_4_percentage': annotation.get_gleason_4_percentage()
                        })
                else:
                    writer.writerow({
                        'case': core.slice.slide.case.id,
                        'slide': core.slice.slide.id,
                        'slice': core.slice.label,
                        'label': core.label,
                        'length': core.length,
                        'area': core.area,
                        'positive': core.is_positive(),
                        'tumor_length': core.tumor_length,
                        'normal_tissue_percentage': core.get_normal_tissue_percentage(),
                        'rois_reviewer': core.slice.annotation_step.rois_annotation.reviewer.username
                    })
        logger.info('Done with core data')

    def _export_focus_regions_info(self, output_folder):
        logger.info('Loading focus region data')
        focus_regions = FocusRegion.objects.all()
        logger.info('Loaded %d focus regions', len(focus_regions))
        logger.info('Saving focus region data')
        header = ['case', 'slide', 'slice', 'core', 'label', 'rois_reviewer', 'clinical_reviewer', 'length', 'area',
                  'cancerous_region', 'core_coverage_percentage', 'perineural_involvement', 'intraductal_carcinoma',
                  'ductal_carcinoma', 'poorly_formed_glands', 'cribriform_pattern', 'small_cell_signet_ring',
                  'hypernephroid_pattern', 'mucinous', 'comedo_necrosis', 'cells_count', 'gleason_4_percentage']
        with open(os.path.join(output_folder, 'focus_regions.csv'), 'w') as ofile:
            writer = DictWriter(ofile, header, delimiter=';')
            writer.writeheader()
            for focus_region in focus_regions:
                annotations = focus_region.clinical_annotations.all()
                if len(annotations) > 0:
                    for annotation in annotations:
                        writer.writerow({
                            'case': focus_region.core.slice.slide.case.id,
                            'slide': focus_region.core.slice.slide.id,
                            'slice': focus_region.core.slice.label,
                            'core': focus_region.core.label,
                            'label': focus_region.label,
                            'length': focus_region.length,
                            'area': focus_region.area,
                            'cancerous_region': focus_region.cancerous_region,
                            'core_coverage_percentage': focus_region.get_core_coverage_percentage(),
                            'rois_reviewer': focus_region.core.slice.annotation_step.rois_annotation.reviewer.username,
                            'clinical_reviewer': annotation.author.username,
                            'perineural_involvement': annotation.perineural_involvement,
                            'intraductal_carcinoma': annotation.intraductal_carcinoma,
                            'ductal_carcinoma': annotation.ductal_carcinoma,
                            'poorly_formed_glands': annotation.poorly_formed_glands,
                            'cribriform_pattern': annotation.cribriform_pattern,
                            'small_cell_signet_ring': annotation.small_cell_signet_ring,
                            'hypernephroid_pattern': annotation.hypernephroid_pattern,
                            'mucinous': annotation.mucinous,
                            'comedo_necrosis': annotation.comedo_necrosis,
                            'cells_count': annotation.cells_count,
                            'gleason_4_percentage': annotation.get_gleason_4_percentage()
                        })
                else:
                    writer.writerow({
                        'case': focus_region.core.slice.slide.case.id,
                        'slide': focus_region.core.slice.slide.id,
                        'slice': focus_region.core.slice.label,
                        'core': focus_region.core.label,
                        'label': focus_region.label,
                        'length': focus_region.length,
                        'area': focus_region.area,
                        'cancerous_region': focus_region.cancerous_region,
                        'core_coverage_percentage': focus_region.get_core_coverage_percentage(),
                        'rois_reviewer': focus_region.core.slice.annotation_step.rois_annotation.reviewer.username
                    })
        logger.info('Done with focus region data')

    def _export_gleason_4_info(self, output_folder):
        logger.info('Loading Gleason 4 data')
        g4_elements = GleasonElement.objects.filter(gleason_type='G4')
        logger.info('Loaded %d Gleason 4 elements', len(g4_elements))
        logger.info('Saving Gleason 4 data')
        header = ['case', 'slide', 'slice', 'core', 'focus_region', 'id', 'clinical_reviewer', 'area', 'cells_count']
        with open(os.path.join(output_folder, 'gleason_4_regions.csv'), 'w') as ofile:
            writer = DictWriter(ofile, header, delimiter=';')
            writer.writeheader()
            for element in g4_elements:
                writer.writerow({
                    'case': element.focus_region_annotation.focus_region.core.slice.slide.case.id,
                    'slide': element.focus_region_annotation.focus_region.core.slice.slide.id,
                    'slice': element.focus_region_annotation.focus_region.core.slice.label,
                    'core': element.focus_region_annotation.focus_region.core.label,
                    'focus_region': element.focus_region_annotation.focus_region.label,
                    'id': element.id,
                    'clinical_reviewer': element.focus_region_annotation.author.username,
                    'area': element.area,
                    'cells_count': element.cells_count
                })
        logger.info('Done with Gleason 4 data')

    def handle(self, *args, **opts):
        output_folder = opts['out_folder']
        if not os.path.isdir(output_folder):
            raise CommandError('"%s" is not a valid folder' % output_folder)
        output_folder = self._create_export_dir(output_folder)
        logger.info('Writing files to folder "%s"', output_folder)
        self._export_bad_quality_slides(output_folder)
        self._export_slices_info(output_folder)
        self._export_cores_info(output_folder)
        self._export_focus_regions_info(output_folder)
        self._export_gleason_4_info(output_folder)
