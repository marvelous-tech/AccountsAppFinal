import csv
from credit.models import CreditFundModel
from expenditure.models import ExpenditureRecordModel
import calendar
from django.core.mail import EmailMessage
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from django.db.models import Sum, F


def get_base_user(request):
    return BaseUserModel.objects.filter(base_user=request.user).first() or \
        BaseUserModel.objects.filter(
            pk=SubUserModel.objects.get(root_user=request.user).base_user_id
        ).first()


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


def get_all_days_of_a_month(year, month):
    year = year
    month = month
    num_days = calendar.monthrange(year, month)[1]
    return [day for day in range(1, num_days + 1)]


def get_credit_amount(request, filters):
    credit_amount = CreditFundModel.object.filter(base_user=get_base_user(request=request), **filters).aggregate(
        sum=Sum(F('amount'))
    )
    return credit_amount['sum']


def on_date_filter_balance(date_filters_credit={}, date_filters_expenditure={}, base_user=1):
    _credit = CreditFundModel.objects.filter(
        base_user=base_user,
        **date_filters_credit,
        is_deleted=False
    ).only('amount')
    _expenditure = ExpenditureRecordModel.objects.filter(
        base_user=base_user,
        **date_filters_expenditure,
        is_deleted=False,
        is_verified=True
    ).only('amount')
    sum_value = _credit.aggregate(
        sum=Sum('amount') - _expenditure.aggregate(sum=Sum('amount'))['sum'])['sum']
    return sum_value or 0


def year_month_lt_balance(year, month, base_user=1):
    return on_date_filter_balance(
        {'fund_added__year': year, 'fund_added__month__lte': month},
        {'expend_date__year': year, 'expend_date__month__lte': month},
        base_user=base_user
    )


def get_credit_model(filters, request, only):
    return CreditFundModel.objects.filter(
        is_deleted=False,
        **filters,
        base_user=get_base_user(request)
    ).only(*only)


def get_expend_model(filters, only, request):
    return ExpenditureRecordModel.objects.filter(
        is_deleted=False,
        **filters,
        base_user=get_base_user(request)
    ).only(*only)


def get_expend_unverified_model(filters, only, request):
    return ExpenditureRecordModel.objects.filter(
        is_deleted=False,
        is_verified=False,
        **filters,
        base_user=get_base_user(request)
    ).only(*only)
