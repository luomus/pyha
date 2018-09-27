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
	req = Request.requests.get(id=requestId)	
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	context = {'req': req, 'time': time, 'req_link': req_link}
	
	if(lang == 'fi'):
		if(req.description != ''):
			subject_content = u"Aineistopyyntö: " + req.description
		else:
			subject_content = u"Aineistopyyntö: " + time
			
		plaintext = get_template('pyha/email/send_mail_after_receiving_request_fi.txt')
	elif(lang == 'en'):
		if(req.description != ''):
			subject_content = u"Download request: " + req.description
		else:
			subject_content = u"Download request: " + time
		plaintext = get_template('pyha/email/send_mail_after_receiving_request_en.txt')
	else:
		if(req.description != ''):
			subject_content = u"På svenska: Aineistopyyntö: " + req.description
		else:
			subject_content = u"På svenska: Aineistopyyntö: " + time
		plaintext = get_template('pyha/email/send_mail_after_receiving_request_sw.txt')
	subject = subject_content	
	from_email = 'helpdesk@laji.fi'	
	to = fetch_email_address(req.user)		
	text_content = plaintext.render(context)
	
	recipients = [to]
	mail = send_mail(subject, text_content, from_email, recipients, fail_silently=False)

def send_mail_after_receiving_download(requestId):
	'''
	Sends email after receiving download from Laji.fi to the person who made the request.
	:param requestId: request identifier
	:param lang: language code
	'''	
	lang = 'fi'
	req = Request.requests.get(id=requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		if(req.description != ''):
			subject_content = u"Aineistopyynnön lataus: " + req.description
		else:
			subject_content = u"Aineistopyynnön lataus: " + time
		message = u"Aineisto on valmiina ladattavaksi.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		if(req.description != ''):
			subject_content = u"Collection ready for download: " + req.description
		else:
			subject_content = u"Collection ready for download: " + time
		message = u"Collection is ready for download.\n\nAddress to your request: "+req_link+"?lang=en" 
	else:
		if(req.description != ''):
			subject_content = u"På svenska: Aineistopyynnön lataus: " + req.description
		else:
			subject_content = u"På svenska: Aineistopyynnön lataus: " + time
		message = u"På svenska: Aineisto on valmiina ladattavaksi.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"
	subject = subject_content
	from_email = 'helpdesk@laji.fi'
	to = fetch_email_address(req.user)
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)

def send_mail_for_approval(requestId, collection, lang):
	'''
	Sends mail to collection download request handler(s) for request approval.
	Also saves their ids to database.
	:param requestId: request identifier 
	:param collection: collection address
	:param lang: language code
	'''	
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	reqCollection = Collection.objects.get(address = collection, request = requestId)
	if(lang == 'fi'):
		subject = "Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = "Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Download request from FinBIF waits for approval decision"
		message = u"Download request sent from Finnish Biodiversity Info Faculty at "+time+" waits for your approval decision.\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"På svenska: Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = u"På svenska: Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
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
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)

	
def send_mail_for_approval_sens(requestId, lang):
	'''
	Sends mail to sensitive information approval request handler(s) for request approval
	:param requestId: request identifier 
	:param lang: language code
	'''	
	username = settings.LAJIPERSONAPI_USER
	password = settings.LAJIPERSONAPI_PW 
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)	
	if(lang == 'fi'):
		subject = "Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = "Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö koskien sensitiivistä aineistoa odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Download request from FinBIF waits for approval decision"
		message = u"Download request sent from Finnish Biodiversity Info Faculty at "+time+" concerning sensitive data waits for your approval decision.\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"På svenska: Aineistopyyntö Lajitietokeskuksesta odottaa hyväksymispäätöstänne"
		message = u"På svenska: Lajitietokeskuksesta "+time+" lähetetty aineistopyyntö koskien sensitiivistä aineistoa odottaa päätöstänne käytön hyväksymisestä.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
	response = requests.get(settings.LAJIPERSONAPI_URL+'/search?type=MA.person&predicatename=MA.role&objectresource=MA.sensitiveInformationApprovalRequestHandler&format=json', auth=HTTPBasicAuth(username, password ))
	recipients = []
	if(response.status_code == 200):
		data = response.json()
		for p in data['rdf:RDF']['MA.person']:
			recipients.append(p['MA.emailAddress'])
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)	
	

def send_mail_after_request_status_change_to_requester(requestId, lang):
	'''
	Sends mail to person who made the request when request status changes
	:param requestId: request identifier 
	:param lang: language code
	'''	
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		subject = u"Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut"
		message = u"Lajitietokeskukseen "+time+" tekemäsi aineistopyynnön tila on muuttunut.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Status change in download request from FinBIF"
		message = u"Status change in request sent from Finnish Biodiversity Info Faculty at "+time+".\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"På svenska: Aineistopyyntösi tila Lajitietokeskuksessa on muuttunut"
		message = u"På svenska: Lajitietokeskukseen "+time+" tekemäsi aineistopyynnön tila on muuttunut.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
	to = fetch_email_address(req.user)
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)
	
def send_mail_after_request_has_been_handled_to_requester(requestId, lang):
	'''
	Sends mail to person who made the request when request has been handled fully
	:param requestId: request identifier 
	:param lang: language code
	'''	
	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		subject = u"Pyyntösi käsittely on valmistunut"
		message = u"Lajitietokeskukseen "+time+" tekemäsi aineistopyyntö on käsitelty.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi"
	elif(lang == 'en'):
		subject = u"Your download request from FinBIF has been handled"
		message = u"Your request from Finnish Biodiversity Info Faculty at "+time+" has been handled.\n\nAddress to the request: "+req_link+"?lang=en"
	else:
		subject = u"Pyyntösi käsittely on valmistunut"
		message = u"På svenska: Lajitietokeskukseen "+time+" tekemäsi aineistopyyntö on käsitelty.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw"	
	from_email = 'helpdesk@laji.fi'
	to = fetch_email_address(req.user)
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)
	
def send_mail_after_additional_information_requested(requestId, lang):

	req = Request.requests.get(id = requestId)
	time = req.date.strftime('%d.%m.%Y %H:%M')
	req_link = settings.REQ_URL+str(req.id)
	if(lang == 'fi'):
		subject = u"Pyyntösi tarvitsee lisätietoja"
		message = u"Lajitietokeskukseen "+time+" tekemäsi aineistopyyntö tarvitsee lisätietoja ennen käsittelyn jatkumista.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=fi&next=information"
	elif(lang == 'en'):
		subject = u"Your download request requires additional information"
		message = u"Your request from Finnish Biodiversity Info Faculty at "+time+" requires additional information.\n\nAddress to the request: "+req_link+"?lang=en&next=information"
	else:
		subject = u"Pyyntösi tarvitsee lisätietoja"
		message = u"På svenska: Lajitietokeskukseen "+time+" tekemäsi aineistopyyntö tarvitsee lisätietoja ennen käsittelyn jatkumista.\n\nOsoite aineistopyyntöön: "+req_link+"?lang=sw&next=information"
	from_email = 'helpdesk@laji.fi'
	to = fetch_email_address(req.user)
	recipients = [to]
	mail = send_mail(subject, message, from_email, recipients, fail_silently=False)























