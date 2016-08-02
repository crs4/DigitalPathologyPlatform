from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
import settings


class IndexView(TemplateView):
    template_name = 'index.html'

    ome_seadragon_base_url = settings.OME_SEADRAGON_STATIC_FILES_URL
    promort_version = settings.PROMORT_VERSION

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super(IndexView, self).dispatch(request, *args, **kwargs)
