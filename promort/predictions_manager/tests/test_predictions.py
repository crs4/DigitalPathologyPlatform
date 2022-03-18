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
import pytest
from django.core.management import call_command
from rois_manager.models import Core, Slice
from predictions_manager.serializers import PredictionSerializer


@pytest.mark.django_db
@pytest.mark.parametrize("slide__image_type", ["MIRAX"])
@pytest.mark.parametrize("n_fragments, n_groups", [(1, 1), (2, 1), (2, 2)])
def test_tissue_to_rois(
    mocker,
    user,
    reviewer,
    tissue_fragments_collection,
    fragments_factory,
    n_fragments,
    n_groups,
):
    fragments_factory(n_fragments, tissue_fragments_collection, n_groups)
    mocker.patch("requests.get", side_effect=mock_requests_get)
    out = ""
    call_command("build_rois_reviews_worklist")
    call_command("tissue_to_rois", username=user.username, stdout=out)
    assert Slice.objects.count() == n_groups
    assert Core.objects.count() == n_fragments * n_groups

    slice_ = Slice.objects.get(pk=1)
    core = Core.objects.get(pk=1)
    assert core.slice == slice_


@pytest.mark.django_db
@pytest.mark.parametrize("n_steps, with_fragments", [(1, 0), (1, 1), (2, 1), (2, 2)])
def test_tissue_to_rois_no_tissue(
    mocker,
    reviewer,
    rois_annotation_steps,
    n_steps,
    with_fragments,
):
    rois_annotation_steps(n_steps, with_fragments)
    mocker.patch("requests.get", side_effect=mock_requests_get)
    call_command("tissue_to_rois", username=reviewer.username)
    assert Core.objects.count() == with_fragments


class MockResponse:
    @property
    def status_code(self):
        return 200

    def json(self):
        return {
            "image_mpp": 0.194475138121547,
            "tile_sources": {
                "Image": {
                    "xmlns": "http://schemas.microsoft.com/deepzoom/2008",
                    "Url": "http://os/ome_seadragon/mirax/deepzoom/get/s_files/",
                    "Format": "jpeg",
                    "Overlap": "1",
                    "TileSize": "256",
                    "Size": {"Height": "100000", "Width": "100000"},
                }
            },
            "slide_bounds": {
                "bounds_x": 10,
                "bounds_y": 10,
                "bounds_height": 100000,
                "bounds_width": 100000,
            },
        }


@pytest.mark.django_db
class TestPredictionSerializer:
    @pytest.mark.parametrize('provenance_data', [False])
    def test_create(self, prediction_data):
        serializer = PredictionSerializer(data=prediction_data)
        assert serializer.is_valid()
        prediction = serializer.save()
        assert prediction.provenance == None

    @pytest.mark.parametrize('provenance_data', [True])
    def test_create_with_provenance(self, prediction_data):
        serializer = PredictionSerializer(data=prediction_data)
        assert serializer.is_valid()
        prediction = serializer.save()
        assert prediction.provenance.model == prediction_data["provenance"]["model"]
        assert prediction.provenance.params == prediction_data["provenance"]["params"]
        assert prediction.provenance.start_date == prediction_data["provenance"]["start_date"]

        assert prediction.provenance.end_date == prediction_data["provenance"]["end_date"]


def mock_requests_get(*args, **kwargs):
    return MockResponse()
