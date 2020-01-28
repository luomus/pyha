from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import translation

class ForceDefaultLanguageMiddleware(MiddlewareMixin):

	def process_request(self, http_request):
		if 'HTTP_ACCEPT_LANGUAGE' in http_request.META:
			del http_request.META['HTTP_ACCEPT_LANGUAGE']
