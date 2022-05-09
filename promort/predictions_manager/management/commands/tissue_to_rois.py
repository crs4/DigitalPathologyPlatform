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
import os
from typing import Dict
from urllib.parse import urljoin

import requests
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from predictions_manager.models import TissueFragment, Prediction
from reviews_manager.models import ROIsAnnotationStep
from rois_manager.models import Core, Slice
from shapely.geometry import Polygon

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
        parser.add_argument(
            "--limit-bounds",
            dest="limit_bounds",
            action="store_true",
            help="apply limit bounds when converting to ROIs",
        )

    def handle(self, *args, **opts):
        logger.info("== Starting import job ==")
        annotation_steps = self._load_annotation_steps(opts["reviewer"])

        if len(annotation_steps) > 0:
            user = self._load_user(opts["username"])

            for step in annotation_steps:
                logger.info("Processing ROIs annotation step %s", step.label)
                latest_prediction = Prediction.objects.filter(
                    slide=step.slide, type='TISSUE'
                ).order_by('-creation_date').first()
                
                fragments_collection = latest_prediction.fragments_collection.order_by('-creation_date').first()
                
                if fragments_collection and fragments_collection.fragments.count() > 0:
                    fragments = fragments_collection.fragments.all()

                    if opts["limit_bounds"]:
                        slide_bounds = self._get_slide_bounds(step.slide)
                    else:
                        slide_bounds = {"bounds_x": 0, "bounds_y": 0}

                    slide_mpp = step.slide.image_microns_per_pixel
                    all_shapes = [json.loads(fragment.shape_json) for fragment in fragments]
                    grouped_shapes = self._group_nearest_cores(all_shapes)
                    for idx, shapes in enumerate(grouped_shapes):
                        slice_label = idx + 1
                        shapes_coords = self._get_slice_coordinates(shapes)

                        slice_obj = self._create_slice(
                            shapes_coords,
                            slice_label,
                            len(shapes),
                            step,
                            user,
                            slide_bounds,
                            fragments_collection
                        )
                        logger.info("Slice saved with ID %d", slice_obj.id)
                        for core_index, core in enumerate(shapes):
                            logger.info(
                                "Loading core %d of %d",
                                core_index + 1,
                                len(shapes),
                            )
                            core_obj = self._create_core(
                                core["coordinates"],
                                core["length"] * slide_mpp,
                                core["area"] * math.pow(slide_mpp, 2),
                                slice_obj,
                                slice_label,
                                core_index + 1,
                                user,
                                slide_bounds,
                                fragments_collection
                            )
                            logger.info("Core saved with ID %d", core_obj.id)
                else:
                    logger.info(
                        "Skipping prediction %s for step %s, no tissue fragment found",
                        latest_prediction.label, step.label,
                    )
                    continue
        else:
            logger.info("== There are no suitable ROIs annotation steps")
        logger.info("== Job completed ==")

    def _get_slice_coordinates(self, shapes):
        polygons = [Polygon(s["coordinates"]) for s in shapes]
        x_min = min([p.bounds[0] for p in polygons])
        y_min = min([p.bounds[1] for p in polygons])
        x_max = max([p.bounds[2] for p in polygons])
        y_max = max([p.bounds[3] for p in polygons])
        return list(
            Polygon(
                [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
            ).exterior.coords
        )

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
        collection
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
            source_collection=collection
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
        collection
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
            source_collection=collection
        )
        core.save()
        return core

    def _get_slide_bounds(self, slide_obj):
        logger.info("Loading bounds for slide %s", slide_obj.id)
        if slide_obj.image_type == "MIRAX":
            req_url = urljoin(
                OME_SEADRAGON_BASE_URL,
                "mirax/deepzoom/get/%s_metadata.json"
                % os.path.splitext(slide_obj.id)[0],
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

    def _get_sorted_cores_map(self, cores):
        cores_map = dict()
        for c in cores:
            bounds = self._get_core_bounds(c)
            cores_map.setdefault((bounds["y_min"], bounds["y_max"]), []).append(c)
        sorted_y_coords = list(cores_map.keys())
        sorted_y_coords.sort(key=lambda x: x[0])
        return cores_map, sorted_y_coords

    def _get_core_bounds(self, core: Dict) -> Dict:
        polygon = Polygon(core["coordinates"])
        bounds = polygon.bounds
        try:
            return {
                "x_min": bounds[0],
                "y_min": bounds[1],
                "x_max": bounds[2],
                "y_max": bounds[3],
            }
        except IndexError:
            raise InvalidPolygonError()

    def _group_nearest_cores(self, cores):
        cores_map, sorted_y_coords = self._get_sorted_cores_map(cores)
        cores_groups = list()
        current_group = cores_map[sorted_y_coords[0]]
        cg_max_y = sorted_y_coords[0][1]
        for i, yc in enumerate(sorted_y_coords[1:]):
            if yc[0] <= cg_max_y:
                current_group.extend(cores_map[yc])
                cg_max_y = max([cg_max_y, yc[1]])
            else:
                cores_groups.append(current_group)
                current_group = cores_map[yc]
                cg_max_y = yc[1]
        cores_groups.append(current_group)
        return cores_groups


class InvalidPolygonError(Exception):
    pass
