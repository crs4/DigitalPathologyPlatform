#  Copyright (c) 2023, CRS4
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

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from clinical_annotations_manager.models import GleasonPattern

from csv import DictWriter

import logging

logger = logging.getLogger("promort_commands")


class Command(BaseCommand):
    help = """
    Export existing Gleason Pattern data to a CSV
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--output_file",
            dest="output",
            type=str,
            required=True,
            help="path of the output CSV file",
        )
        parser.add_argument(
            "--page_size",
            dest="page_size",
            type=int,
            default=0,
            help="the number of records retrieved for each page (this will enable pagination)",
        )

    def _dump_row(self, gleason_pattern, csv_writer):
        try:
            action_start_time = gleason_pattern.action_start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except AttributeError:
            action_start_time = None
        try:
            action_complete_time = gleason_pattern.action_complete_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except AttributeError:
            action_complete_time = None
        csv_writer.writerow(
            {
                "case_id": gleason_pattern.annotation_step.slide.case.id,
                "slide_id": gleason_pattern.annotation_step.slide.id,
                "clinical_review_step_id": gleason_pattern.annotation_step.label,
                "reviewer": gleason_pattern.author.username,
                "focus_region_id": gleason_pattern.focus_region.id,
                "focus_region_label": gleason_pattern.focus_region.label,
                "action_start_time": action_start_time,
                "action_completion_time": action_complete_time,
                "creation_date": gleason_pattern.creation_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "gleason_pattern_id": gleason_pattern.id,
                "gleason_pattern_label": gleason_pattern.label,
                "gleason_type": gleason_pattern.gleason_type,
                "area": gleason_pattern.area,
                "subregions_count": gleason_pattern.subregions.count(),
            }
        )

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info(f"Pagination enabled ({page_size} records for page)")
            g_el_qs = GleasonPattern.objects.get_queryset().order_by("creation_date")
            paginator = Paginator(g_el_qs, page_size)
            for x in paginator.page_range:
                logger.info(f"-- page {x} --")
                page = paginator.page(x)
                for g_el in page.object_list:
                    self._dump_row(g_el, csv_writer)
        else:
            logger.info("Loading full batch")
            gleason_patterns = GleasonPattern.objects.all()
            for g_el in gleason_patterns:
                self._dump_row(g_el, csv_writer)

    def _export_data(self, out_file, page_size):
        header = [
            "case_id",
            "slide_id",
            "clinical_review_step_id",
            "reviewer",
            "focus_region_id",
            "focus_region_label",
            "gleason_pattern_id",
            "gleason_pattern_label",
            "action_start_time",
            "action_completion_time",
            "creation_date",
            "gleason_type",
            "area",
            "subregions_count",
        ]
        with open(out_file, "w") as ofile:
            writer = DictWriter(ofile, delimiter=",", fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info("=== Starting export job ===")
        self._export_data(opts["output"], opts["page_size"])
        logger.info("=== Data saved to %s ===", opts["output"])
