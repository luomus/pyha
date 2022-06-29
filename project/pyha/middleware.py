from django.utils.deprecation import MiddlewareMixin


class ForceDefaultLanguageMiddleware(MiddlewareMixin):

    def process_request(self, http_request):
        if 'HTTP_ACCEPT_LANGUAGE' in http_request.META:
            del http_request.META['HTTP_ACCEPT_LANGUAGE']


class NoCache(MiddlewareMixin):

    def process_response(self, request, response):
        """
        set the "Cache-Control" header to "must-revalidate, no-cache"
        """
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'must-revalidate, no-cache'
        return response
