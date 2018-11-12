		
def check_language(request):
	if request.GET.get('lang') and request.session.get('_language', "none") != request.GET.get('lang'):
			request.session["_language"] = request.GET.get('lang')
			return True
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