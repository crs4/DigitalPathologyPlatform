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

import json
import logging
import math
from urllib.parse import urljoin

import requests
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from predictions_manager.models import TissueFragment
from reviews_manager.models import ROIsAnnotationStep
from rois_manager.models import Core, Slice

from promort.settings import OME_SEADRAGON_BASE_URL

logger = logging.getLogger("promort_commands")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            dest="username",
            type=str,
            required=True,
            help="user that will create the new ROIs",
        )
        parser.add_argument(
            "--reviewer",
            dest="reviewer",
            type=str,
            required=False,
            default=None,
            help="apply only to ROIs annotation steps assigned to this reviewer",
        )

    def handle(self, *args, **opts):
        logger.info("== Starting import job ==")
        annotation_steps = self._load_annotation_steps(opts["reviewer"])

        if len(annotation_steps) > 0:
            user = self._load_user(opts["username"])
            slide_bounds = None

            for step in annotation_steps:
                logger.info("Processing ROIs annotation step %s", step.label)
                fragments = TissueFragment.objects.filter(
                    collection__prediction__slide=step.slide
                )

                if slide_bounds is None:
                    slide_bounds = self._get_slide_bounds(step.slide)
                for slice_index, slice in enumerate(fragments):
                    logger.info(
                        "Loading slice %d of %d", slice_index + 1, len(fragments)
                    )
                    slide_mpp = step.slide.image_microns_per_pixel
                    slice_obj = self._create_slice(
                        slice["coordinates"],
                        slice_index + 1,
                        len(slice["cores"]),
                        step,
                        user,
                        slide_bounds,
                    )
                    logger.info("Slice saved with ID %d", slice_obj.id)
                    for core_index, core in enumerate(slice["cores"]):
                        logger.info(
                            "Loading core %d of %d",
                            core_index + 1,
                            len(slice["cores"]),
                        )
                        core_obj = self._create_core(
                            core["coordinates"],
                            core["length"] * slide_mpp,
                            core["area"] * math.pow(slide_mpp, 2),
                            slice_obj,
                            slice_index + 1,
                            core_index + 1,
                            user,
                            slide_bounds,
                        )
                        logger.info("Core saved with ID %d", core_obj.id)
        else:
            logger.info("== There are no suitable ROIs annotation steps")
        logger.info("== Job completed ==")

    def _load_annotation_steps(self, reviewer=None):
        filter_ = {"start_date__isnull": True}
        if reviewer:
            logger.info("Filter steps assigned to reviewer %s", reviewer)
            filter_["rois_annotation__reviewer__username"] = reviewer

        annotations_steps = ROIsAnnotationStep.objects.filter(**filter_)
        logger.info("Loaded %d ROIs annotation steps" % len(annotations_steps))
        return annotations_steps

    def _adjust_roi_coordinates(self, roi_coordinates, slide_bounds):
        new_coordinates = list()
        for rc in roi_coordinates:
            new_coordinates.append(
                (
                    rc[0] - int(slide_bounds["bounds_x"]),
                    rc[1] - int(slide_bounds["bounds_y"]),
                )
            )
        return new_coordinates

    def _create_roi_json(self, roi_coordinates, shape_id, stroke_color):
        return {
            "fill_color": "#ffffff",
            "fill_alpha": 0.01,
            "hidden": False,
            "segments": [{"point": {"x": rc[0], "y": rc[1]}} for rc in roi_coordinates],
            "shape_id": shape_id,
            "stroke_alpha": 1,
            "stroke_color": stroke_color,
            "stroke_width": 40,
            "type": "polygon",
        }

    def _create_slice(
        self,
        slice_coordinates,
        slice_id,
        cores_count,
        annotation_step,
        user,
        slide_bounds,
    ):
        slice_coordinates = self._adjust_roi_coordinates(
            slice_coordinates, slide_bounds
        )
        roi_json = self._create_roi_json(
            slice_coordinates, "slice_s%02d" % slice_id, "#000000"
        )
        slice_ = Slice(
            label=roi_json["shape_id"],
            annotation_step=annotation_step,
            slide=annotation_step.slide,
            author=user,
            roi_json=json.dumps(roi_json),
            total_cores=cores_count,
        )
        slice_.save()
        return slice_

    def _create_core(
        self,
        core_coordinates,
        core_length,
        core_area,
        slice_,
        slice_id,
        core_id,
        user,
        slide_bounds,
    ):
        core_coordinates = self._adjust_roi_coordinates(core_coordinates, slide_bounds)
        roi_json = self._create_roi_json(
            core_coordinates, "core_s%02d_c%02d" % (slice_id, core_id), "#0000ff"
        )
        core = Core(
            label=roi_json["shape_id"],
            slice=slice_,
            author=user,
            roi_json=json.dumps(roi_json),
            length=core_length,
            area=core_area,
        )
        core.save()
        return core

    def _get_slide_bounds(self, slide_obj):
        logger.info("Loading bounds for slide %s", slide_obj.id)
        if slide_obj.image_type == "MIRAX":
            req_url = urljoin(
                OME_SEADRAGON_BASE_URL,
                "mirax/deepzoom/get/%s_metadata.json" % slide_obj.id,
            )
        elif slide_obj.image_type == "OMERO_IMG":
            req_url = urljoin(
                OME_SEADRAGON_BASE_URL,
                "deepzoom/get/%d_metadata.json" % slide_obj.omero_id,
            )
        else:
            raise CommandError(
                "Unable to handle images with image_type %s" % slide_obj.image_type
            )
        response = requests.get(req_url)
        logger.info("response.status_code %s", response.status_code)
        if response.status_code == requests.codes.OK:
            slide_details = response.json()
            return slide_details["slide_bounds"]
        else:
            logger.error("Unable to load slide details from OMERO server")
            raise CommandError("Unable to load slide details from OMERO server")

    def _load_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error("There is no user with username %s", username)
            raise CommandError("There is no user with username %s" % username)
