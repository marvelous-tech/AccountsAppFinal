import csv
from django.core.mail import EmailMessage
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def sum_int_of_array(array):
    sum_of_array = 0

    for value in array:
        sum_of_array = sum_of_array + value
    return sum_of_array


def django_generate_csv_from_model_object(file_obj, query_set, headings, attributes):

    writer = csv.writer(file_obj, delimiter=',')
    writer.writerow(headings)

    for obj in query_set:
        writer.writerow([obj.__getattribute__(name) for name in attributes])
    return writer


def django_download_generated_csv_from_model_object(file_name, query_set, headings, attributes):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    django_generate_csv_from_model_object(response, query_set, headings, attributes)
    return response


def django_send_email(subject, body, from_email, to, fail_silently=False):
    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to)
    return email.send(fail_silently=fail_silently)


def django_send_email_with_attachments(subject, body, from_email, to, file_name, content, mimetype, fail_silently=False):

    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to)
    email.attach(filename=file_name, content=content, mimetype=mimetype)
    email.send(fail_silently=fail_silently)
    return email


def django_render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
