from django_filters import rest_framework as filters
from expenditure.models import ExpenditureRecordModel


class ExpenditureRecordFilter(filters.FilterSet):
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    added = filters.DateFromToRangeFilter()
    expend_date = filters.DateFromToRangeFilter()
    added_date = filters.DateFilter(field_name='added', lookup_expr='date')
    heading = filters.CharFilter(field_name='expend_heading__heading_name', lookup_expr='icontains')

    class Meta:
        model = ExpenditureRecordModel
        fields = (
            'is_verified', 
            'amount',
            'max_amount', 
            'min_amount', 
            'added', 
            'expend_date', 
            'added_date',
            'heading'
            )
