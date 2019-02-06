from django_filters import rest_framework as filters
from credit.models import CreditFundModel


class CreditFundFilter(filters.FilterSet):
    fund_source = filters.CharFilter(field_name='source__source_name', lookup_expr='icontains')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    added = filters.DateFromToRangeFilter()

    class Meta:
        model = CreditFundModel
        fields = (
            'fund_source',
            'amount',
            'added',
            'max_amount',
            'min_amount'
        )
