from pyha.warehouse import fetch_pdf, show_filters
from pyha.database import get_request_contacts, get_collection_list, get_reasons
from django.template.loader import get_template
from pyha.roles import HANDLER_ANY
from pyha.models import Request


def get_request_summary_pdf(request_id, lang):
    user_request = Request.objects.get(id=request_id)

    context = {
        'user_request': user_request,
        'contactlist': get_request_contacts(user_request),
        'collections': get_collection_list(user_request, lang),
        'role': HANDLER_ANY,
        'reasonlist': get_reasons(user_request),
        'filters': show_filters(user_request, lang)
    }

    template_path = 'pyha/request_summary_pdf/request_summary_pdf.html'

    pdf_response = fetch_pdf(get_template(template_path).render(context), None)
    if not pdf_response:
        raise Exception('Request summary pdf generation failed')
    return pdf_response.content
