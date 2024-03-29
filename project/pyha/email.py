# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.utils import translation
from django.utils.translation import ugettext
from pyha.warehouse import fetch_email_address
from django.template.loader import get_template
from pyha.models import Request
from django.utils.translation import ugettext


def send_raw_mail(subject, sender, recipients, content):
    mail = send_mail(subject, content, sender, recipients, fail_silently=False)


def send_mail_after_receiving_request(requestId, lang):
    '''
    Sends email after receiving request from Laji.fi to the person who made the request.
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('mail_after_receiving_request_subject'),
            'mail_after_receiving_request'
        )


def send_mail_after_approving_terms(requestId, lang):
    '''
    Sends email after the user has approved terms
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('mail_after_accepting_terms_subject'),
            'mail_after_accepting_terms'
        )


def send_mail_after_receiving_download(requestId, lang):
    '''
    Sends email after receiving download from Laji.fi to the person who made the request.
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('mail_after_receiving_download_subject'),
            'mail_after_receiving_download'
        )


def send_mail_after_request_status_change_to_requester(requestId, lang):
    '''
    Sends mail to person who made the request when request status changes
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('mail_after_request_status_change_to_requester_subject'),
            'mail_after_request_status_change_to_requester'
        )


def send_mail_after_request_has_been_handled_to_requester(requestId, lang):
    '''
    Sends mail to person who made the request when request has been handled fully
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('mail_after_request_has_been_handled_to_requester_subject'),
            'mail_after_request_has_been_handled_to_requester'
        )


def send_mail_after_additional_information_requested(requestId, lang):
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('mail_after_additional_information_requested_subject'),
            'mail_after_additional_information_requested'
        )


def send_status_mail_to_requester(requestId, accepted, declined, pending, lang):
    with translation.override(lang):
        _send_mail_to_request_user(
            requestId,
            lang,
            ugettext('status_mail_to_requester_subject'),
            'status_mail_to_requester',
            {'accepted': accepted, 'declined': declined, 'pending': pending}
        )


def send_mail_for_missing_handlers(collections_missing_handler, lang='fi'):
    '''
    Sends email after receiving request from Laji.fi to ICT if there are no collection handlers for a request.
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        context = {'collections_missing_handler': collections_missing_handler}

        subject = ugettext('mail_collections_missing_handlers_subject')
        text_content = _get_email_content('mail_collections_missing_handlers', lang, context)
        from_email = settings.PYHA_EMAIL
        to = [settings.ICT_EMAIL]

        mail = send_mail(subject, text_content, from_email, to, fail_silently=False)


def get_template_of_mail_for_approval(requestId, lang):
    '''
    Sends mail to collection download request handler(s) for request approval.
    Also saves their ids to database.
    :param requestId: request identifier
    :param collection: collection address
    :param lang: language code
    '''
    with translation.override(lang):
        context = _get_request_context(requestId)

        subject = ugettext('mail_for_approval_subject')
        text_content = _get_email_content('mail_for_approval', lang, context)
        from_email = settings.ICT_EMAIL

        template = {'header': subject, 'content': text_content, 'sender': from_email}
        return template


def send_mail_about_new_request_to_handlers(requestId, users, lang='fi'):
    from pyha.pdf_files import get_request_summary_pdf
    '''
    Sends email after the user has approved terms to handler(s)
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        context = _get_request_context(requestId)

        subject = ugettext('mail_for_approval_subject')
        text_content = _get_email_content('mail_for_approval', lang, context)
        from_email = settings.ICT_EMAIL
        to = [fetch_email_address(userId) for userId in users]

        summary_pdf = get_request_summary_pdf(requestId, lang)
        summary_pdf_name = '{} {}.pdf'.format(ugettext('request_summary_for_handlers'), requestId)
        summary_pdf_name = summary_pdf_name.replace(' ', '_')

        email = EmailMessage(subject, text_content, from_email, to)
        email.attach(summary_pdf_name, summary_pdf, 'application/pdf')
        email.send(fail_silently=False)


def send_mail_after_additional_information_received(requestId, users, lang='fi'):
    '''
    Sends email to request handler(s) or admin(s) who has requested additional information after the user has provided it.
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        context = _get_request_context(requestId)

        subject = ugettext('mail_after_additional_information_received_subject')
        text_content = _get_email_content('mail_after_additional_information_received', lang, context)
        from_email = settings.ICT_EMAIL
        to = [fetch_email_address(userId) for userId in users]

        mail = send_mail(subject, text_content, from_email, to, fail_silently=False)


def send_mail_for_unchecked_requests(userId, request_ids, lang='fi'):
    '''
    Sends email after receiving request from Laji.fi to the person who made the request.
    :param requestId: request identifier
    :param lang: language code
    '''
    send_mail_for_unchecked_requests_to_email(fetch_email_address(userId), request_ids, lang)


def send_mail_for_unchecked_requests_to_email(mailto, request_ids, lang='fi'):
    with translation.override(lang):
        req_links = ['{}request/{}'.format(settings.PYHA_URL, str(req_id)) for req_id in request_ids]

        context = {
            'count': len(request_ids),
            'req_links': req_links
        }

        subject = ugettext('mail_for_unchecked_requests_subject')
        text_content = _get_email_content('mail_for_unchecked_requests', lang, context)
        from_email = settings.ICT_EMAIL
        to = [mailto]

        mail = send_mail(subject, text_content, from_email, to, fail_silently=False)


def send_admin_mail_after_approved_request(requestId, mailto, lang='fi'):
    '''
    Sends email to admin after approved by the person who made the request.
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        context = _get_request_context(requestId)

        subject = ugettext('mail_admin_after_request_approval_subject').format(**context)
        text_content = _get_email_content('mail_admin_after_request_approval', lang, context)
        from_email = settings.PYHA_EMAIL
        to = [mailto]

        mail = send_mail(subject, text_content, from_email, to, fail_silently=False)


def send_admin_mail_after_approved_request_missing_handlers(requestId, mailto, lang='fi'):
    '''
    Sends email to admin after approved by the person who made the request.
    :param requestId: request identifier
    :param lang: language code
    '''
    with translation.override(lang):
        context = _get_request_context(requestId)

        subject = ugettext('mail_admin_after_request_approval_missing_handlers_subject').format(**context)
        text_content = _get_email_content('mail_admin_after_request_approval_missing_handlers', lang, context)
        from_email = settings.PYHA_EMAIL
        to = [mailto]

        mail = send_mail(subject, text_content, from_email, to, fail_silently=False)


def _send_mail_to_request_user(requestId, lang, plain_subject, template_name, context={}):
    context = {**_get_request_context(requestId), **context}

    subject = plain_subject.format(**context).replace('\n', ' ')
    text_content = _get_email_content(template_name, lang, context)
    from_email = settings.ICT_EMAIL
    to = [fetch_email_address(context['req'].user)]

    mail = send_mail(subject, text_content, from_email, to, fail_silently=False)


def _get_email_content(template_name, lang, context):
    template = get_template('pyha/email/{}_{}.txt'.format(template_name, lang))
    return template.render(context)


def _get_request_context(requestId):
    req = Request.objects.get(id=requestId)
    time = req.date.strftime('%d.%m.%Y %H:%M')
    context = {
        'req': req,
        'time': time,
        'req_link': '{}request/{}'.format(settings.PYHA_URL, str(req.id)),
        'description_or_time': req.description if req.description != '' else time,
        'manual_link': '{}handler-manual.pdf'.format(settings.PYHA_URL)
    }
    return context
