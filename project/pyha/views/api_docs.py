from apispec import APISpec
from apispec import BasePlugin
from apispec.yaml_utils import load_operations_from_docstring
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from pyha.views.api_statistics import request_count_by_year, collection_counts, request_reason_counts, \
    request_reason_phrase_counts, request_party_involvement_counts


class PyhaPlugin(BasePlugin):
    def path_helper(self, path, operations, func, **kwargs):
        """Path helper that parses docstrings for operations. Adds a
        ``func`` parameter to `apispec.APISpec.path`.
        """
        operations.update(load_operations_from_docstring(func.__doc__))


def get_spec():
    spec = APISpec(
        title="Pyha API",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[PyhaPlugin()]
    )

    spec.path(path=reverse('pyha:count_by_year'), func=request_count_by_year)
    spec.path(path=reverse('pyha:collection_counts'), func=collection_counts)
    spec.path(path=reverse('pyha:reason_counts'), func=request_reason_counts)
    spec.path(path=reverse('pyha:reason_phrase_counts'), func=request_reason_phrase_counts)
    spec.path(path=reverse('pyha:party_involvement_counts'), func=request_party_involvement_counts)

    return spec


@csrf_exempt
def api_spec(http_request):
    return JsonResponse(get_spec().to_dict())


@csrf_exempt
def api_docs(http_request):
    return render(http_request, 'pyha/swagger/swaggerui.html', {'static': settings.STA_URL, 'version': settings.VERSION})
