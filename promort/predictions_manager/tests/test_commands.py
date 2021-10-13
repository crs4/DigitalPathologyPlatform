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


@pytest.mark.django_db
@pytest.mark.parametrize("slide__image_type", ["MIRAX"])
@pytest.mark.parametrize("n_fragments", [1, 2])
def test_tissue2roi(
    mocker, user, reviewer, tissue_fragments_collection, fragments_factory, n_fragments
):
    fragments_factory(n_fragments, tissue_fragments_collection)
    mocker.patch("requests.get", side_effect=mock_requests_get)
    out = ""
    call_command("build_rois_reviews_worklist")
    call_command("tissue2roi", username=user.username, stdout=out)
    assert Slice.objects.count() == 1
    assert Core.objects.count() == n_fragments

    slice_ = Slice.objects.get(pk=1)
    core = Core.objects.get(pk=1)
    assert core.slice == slice_


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


def mock_requests_get(*args, **kwargs):
    return MockResponse()
