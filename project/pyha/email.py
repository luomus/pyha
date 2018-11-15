#coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

from pyha.models import Collection, Request
from pyha.warehouse import fetch_email_address
import requests
from requests.auth import HTTPBasicAuth


def send_mail_after_receiving_request(requestId, lang):
	'''
	Sends email after receiving request from Laji.fi to the person who made the request.
	:param requestId: request identifier
	:param lang: language code
	'''	
	req = Request.objects.get(id=requestId)	
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)
	context = {'req': req, 'time': time, 'req_link': req_link}
	
	if(lang == 'fi'):
		if(req.description != ''):
			subject_content = u"Aineistopyyntö: " + req.description
		else:
			subject_content = u"Aineistopyyntö: " + time
			
		plaintext = get_template('pyha/email/mail_after_receiving_request_fi.txt')
	elif(lang == 'en'):
		if(req.description != ''):
			subject_content = u"Download request: " + req.description
		else:
			subject_content = u"Download request: " + time
		plaintext = get_template('pyha/email/mail_after_receiving_request_en.txt')
	else:
		if(req.description != ''):
			subject_content = u"På svenska: Aineistopyyntö: " + req.description
		else:
			subject_content = u"På svenska: Aineistopyyntö: " + time
		plaintext = get_template('pyha/email/mail_after_receiving_request_sv.txt')
	subject = subject_content	
	from_email = settings.ICT_EMAIL
	to = fetch_email_address(req.user)		
	text_content = plaintext.render(context)
	
	recipients = [to]
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)
	
def send_mail_for_missing_handlers(collections_missing_handler, lang):
	'''
	Sends email after receiving request from Laji.fi to ICT if there are no collection handlers for a request.
	:param requestId: request identifier
	:param lang: language code
	'''	
	context = {'collections_missing_handler': collections_missing_handler}
	
	if(lang == 'fi'):
		subject_content = u"Kokoelmista puuttuu käsittelijöitä."
		plaintext = get_template('pyha/email/mail_collections_missing_handlers_fi.txt')
	elif(lang == 'en'):
		subject_content = u"Collections are missing handlers."
		plaintext = get_template('pyha/email/mail_collections_missing_handlers_en.txt')
	else:
		subject_content = u"På svenska: Kokoelmista puuttuu käsittelijöitä."
		plaintext = get_template('pyha/email/mail_collections_missing_handlers_sv.txt')
	subject = subject_content	
	from_email = settings.PYHA_EMAIL
	to = settings.ICT_EMAIL
	text_content = plaintext.render(context)
	
	recipients = [to]
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)


def send_mail_after_receiving_download(requestId, lang):
	'''
	Sends email after receiving download from Laji.fi to the person who made the request.
	:param requestId: request identifier
	:param lang: language code
	'''	
	req = Request.objects.get(id=requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)
	context = {'req': req, 'time': time, 'req_link': req_link}
	if(lang == 'fi'):
		if(req.description != ''):
			subject_content = u"Aineistopyynnön lataus: " + req.description
		else:
			subject_content = u"Aineistopyynnön lataus: " + time
		plaintext = get_template('pyha/email/mail_after_receiving_download_fi.txt')
	elif(lang == 'en'):
		if(req.description != ''):
			subject_content = u"Collection ready for download: " + req.description
		else:
			subject_content = u"Collection ready for download: " + time
		plaintext = get_template('pyha/email/mail_after_receiving_download_en.txt')
	else:
		if(req.description != ''):
			subject_content = u"På svenska: Aineistopyynnön lataus: " + req.description
		else:
			subject_content = u"På svenska: Aineistopyynnön lataus: " + time
		plaintext = get_template('pyha/email/mail_after_receiving_download_sv.txt')
	subject = subject_content
	from_email = settings.ICT_EMAIL
	to = fetch_email_address(req.user)
	text_content = plaintext.render(context)
	
	recipients = [to]
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)

def send_mail_for_approval(requestId, collection, lang):
	'''
	Sends mail to collection download request handler(s) for request approval.
	Also saves their ids to database.
	:param requestId: request identifier 
	:param collection: collection address
	:param lang: language code
	'''	
	req = Request.objects.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)
	reqCollection = Collection.objects.get(address = collection, request = requestId)
	context = {'req': req, 'time': time, 'req_link': req_link, 'reqCollection': reqCollection}
	if(lang == 'fi'):
		subject = "Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		plaintext = get_template('pyha/email/mail_for_approval_fi.txt')
	elif(lang == 'en'):
		subject = u"Download request from FinBIF waits for approval decision"
		plaintext = get_template('pyha/email/mail_for_approval_en.txt')
	else:
		subject = u"På svenska: Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		plaintext = get_template('pyha/email/mail_for_approval_sv.txt')
	from_email = settings.ICT_EMAIL
	recipients = []
	response = requests.get(settings.LAJIAPI_URL+"collections/"+str(collection)+"?access_token="+settings.LAJIAPI_TOKEN)
	if(response.status_code == 200):
		data = response.json()
		if 'downloadRequestHandler' in data:
			handlers = data['downloadRequestHandler']
			reqCollection.downloadRequestHandler = handlers
			for personId in handlers:
				email = fetch_email_address(personId)
				recipients.append(email)
	text_content = plaintext.render(context)
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)

	
def send_mail_for_approval_sens(requestId, lang):
	'''
	Sends mail to sensitive information approval request handler(s) for request approval
	:param requestId: request identifier 
	:param lang: language code
	'''	
	username = settings.LAJIPERSONAPI_USER
	password = settings.LAJIPERSONAPI_PW 
	req = Request.objects.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)	
	context = {'req': req, 'time': time, 'req_link': req_link}
	if(lang == 'fi'):
		subject = "Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		plaintext = get_template('pyha/email/mail_for_approval_sens_fi.txt')
	elif(lang == 'en'):
		subject = u"Download request from FinBIF waits for approval decision"
		plaintext = get_template('pyha/email/mail_for_approval_sens_en.txt')
	else:
		subject = u"På svenska: Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		plaintext = get_template('pyha/email/mail_for_approval_sens_sv.txt')
	from_email = settings.ICT_EMAIL
	response = requests.get(settings.LAJIPERSONAPI_URL+'/search?type=MA.person&predicatename=MA.role&objectresource=MA.sensitiveInformationApprovalRequestHandler&format=json', auth=HTTPBasicAuth(username, password ))
	recipients = []
	if(response.status_code == 200):
		data = response.json()
		for p in data['rdf:RDF']['MA.person']:
			recipients.append(p['MA.emailAddress'])
	text_content = plaintext.render(context)
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)	
	

def send_mail_after_request_status_change_to_requester(requestId, lang):
	'''
	Sends mail to person who made the request when request status changes
	:param requestId: request identifier 
	:param lang: language code
	'''	
	req = Request.objects.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)
	context = {'req': req, 'time': time, 'req_link': req_link}
	if(lang == 'fi'):
		subject = u"Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut"
		plaintext = get_template('pyha/email/mail_after_request_status_change_to_requester_fi.txt')
	elif(lang == 'en'):
		subject = u"Status change in download request from FinBIF"
		plaintext = get_template('pyha/email/mail_after_request_status_change_to_requester_en.txt')
	else:
		subject = u"På svenska: Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut"
		plaintext = get_template('pyha/email/mail_after_request_status_change_to_requester_sv.txt')
	from_email = settings.ICT_EMAIL
	to = fetch_email_address(req.user)
	recipients = [to]
	text_content = plaintext.render(context)
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)
	
def send_mail_after_request_has_been_handled_to_requester(requestId, lang):
	'''
	Sends mail to person who made the request when request has been handled fully
	:param requestId: request identifier 
	:param lang: language code
	'''	
	req = Request.objects.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)
	context = {'req': req, 'time': time, 'req_link': req_link}
	if(lang == 'fi'):
		subject = u"Pyyntösi käsittely on valmistunut"
		plaintext = get_template('pyha/email/mail_after_request_has_been_handled_to_requester_fi.txt')
	elif(lang == 'en'):
		subject = u"Your download request from FinBIF has been handled"
		plaintext = get_template('pyha/email/mail_after_request_has_been_handled_to_requester_en.txt')
	else:
		subject = u"På svenska: Pyyntösi käsittely on valmistunut"
		plaintext = get_template('pyha/email/mail_after_request_has_been_handled_to_requester_sv.txt')	
	from_email = settings.ICT_EMAIL
	to = fetch_email_address(req.user)
	recipients = [to]
	text_content = plaintext.render(context)
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)
	
def send_mail_after_additional_information_requested(requestId, lang):

	req = Request.objects.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.PYHA_URL+"request/"+str(req.id)
	context = {'req': req, 'time': time, 'req_link': req_link}
	if(lang == 'fi'):
		subject = u"Pyyntösi tarvitsee lisätietoja"
		plaintext = get_template('pyha/email/mail_after_request_has_been_handled_to_requester_fi.txt')
	elif(lang == 'en'):
		subject = u"Your download request requires additional information"
		plaintext = get_template('pyha/email/mail_after_request_has_been_handled_to_requester_en.txt')
	else:
		subject = u"På svenska: Pyyntösi tarvitsee lisätietoja"
		plaintext = get_template('pyha/email/mail_after_request_has_been_handled_to_requester_sv.txt')
	from_email = settings.ICT_EMAIL
	to = fetch_email_address(req.user)
	recipients = [to]
	text_content = plaintext.render(context)
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)

def send_mail_for_unchecked_requests(userId, count, lang):
	'''
	Sends email after receiving request from Laji.fi to the person who made the request.
	:param requestId: request identifier
	:param lang: language code
	'''	
	req_link = settings.PYHA_URL
	context = {'count': count, 'pyha_link': settings.PYHA_URL}
	
	if(lang == 'fi'):
		subject_content = u"Laji.fi:hin on tullut uusia aineistopyyntöjä"
		plaintext = get_template('pyha/email/mail_for_unchecked_requests_fi.txt')
	elif(lang == 'en'):
		subject_content = u"FinBIF has received new requests which require your attention"
		plaintext = get_template('pyha/email/mail_for_unchecked_requests_en.txt')
	else:
		subject_content = u"På svenska: Laji.fi:hin on tullut uusia aineistopyyntöjä"
		plaintext = get_template('pyha/email/mail_for_unchecked_requests_sv.txt')
	subject = subject_content	
	from_email = settings.ICT_EMAIL
	to = fetch_email_address(userId)		
	text_content = plaintext.render(context)	
	
	recipients = [to]
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)

















