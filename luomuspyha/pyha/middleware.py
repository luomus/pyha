from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import translation

class ForceDefaultLanguageMiddleware(MiddlewareMixin):

	def process_request(self, request):
		if 'HTTP_ACCEPT_LANGUAGE' in request.META:
			del request.META['HTTP_ACCEPT_LANGUAGE']
