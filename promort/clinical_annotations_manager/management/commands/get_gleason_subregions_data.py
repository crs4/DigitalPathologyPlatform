#  Copyright (c) 2021, CRS4
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
from clinical_annotations_manager.models import GleasonPatternSubregion

from csv import DictWriter

import logging, json

logger = logging.getLogger("promort_commands")


class Command(BaseCommand):
    help = """
    Export existing Gleason Pattern subregions data to a CSV
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

    def _dump_row(self, gleason_subregion, csv_writer):
        gp = gleason_subregion.gleason_pattern
        csv_writer.writerow(
            {
                "case_id": gp.annotation_step.slide.case.id,
                "slide_id": gp.annotation_step.slide.id,
                "clinical_review_step_id": gp.annotation_step.label,
                "reviewer": gp.author.username,
                "focus_region_id": gp.focus_region.id,
                "gleason_pattern_id": gp.id,
                "gleason_pattern_label": gp.label,
                "creation_date": gleason_subregion.creation_date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "subregion_id": gleason_subregion.id,
                "subregion_label": gleason_subregion.label,
                "type": json.loads(gleason_subregion.details_json)["type"],
                "area": gleason_subregion.area,
            }
        )

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info(f"Pagination enabled ({page_size} records for page)")
            g_el_qs = GleasonPatternSubregion.objects.get_queryset().order_by(
                "creation_date"
            )
            paginator = Paginator(g_el_qs, page_size)
            for x in paginator.page_range:
                logger.info(f"-- page {x} --")
                page = paginator.page(x)
                for g_el in page.object_list:
                    self._dump_row(g_el, csv_writer)
        else:
            logger.info("Loading full batch")
            gleason_patterns = GleasonPatternSubregion.objects.all()
            for g_el in gleason_patterns:
                self._dump_row(g_el, csv_writer)

    def _export_data(self, out_file, page_size):
        header = [
            "case_id",
            "slide_id",
            "clinical_review_step_id",
            "reviewer",
            "focus_region_id",
            "gleason_pattern_id",
            "gleason_pattern_label",
            "creation_date",
            "subregion_id",
            "subregion_label",
            "type",
            "area",
        ]
        with open(out_file, "w") as ofile:
            writer = DictWriter(ofile, delimiter=",", fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info("=== Starting export job ===")
        self._export_data(opts["output"], opts["page_size"])
        logger.info(f"=== Data saved to {opts['output']}===")
