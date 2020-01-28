from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import get_language
from django.utils import translation
from django.conf import settings

def check_language(request):
	return False

def translate_truth(value, lang):
	if value == "true":
		if(lang == 'fi'):
			value = "Kyllä"
		if(lang == 'en'):
			value = "Yes"
		if(lang == 'sv'):
			value = "Ja"
	elif value == "false":
		if(lang == 'fi'):
			value = "Ei"
		if(lang == 'en'):
			value = "No"
		if(lang == 'sv'):
			value = "Nej"
	return value
