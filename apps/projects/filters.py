import django_filters
from django import forms
from django.db.models import Avg
from django.forms.widgets import ChoiceWidget
from django_filters import (
    CharFilter,
    ModelChoiceFilter,
    ChoiceFilter,
    DateFromToRangeFilter,
    NumericRangeFilter, NumberFilter
)
from django_filters.widgets import RangeWidget, LookupChoiceWidget

from config.constants import EQUIPMENT_TYPES
from .models import Equipment, Manufacture, Location


def get_countries():
    countries_list = Location.objects.values_list('country', flat=True).distinct().order_by('country')
    result_list = [[country, country] for country in countries_list]

    return result_list


def get_cities():
    cities_list = Location.objects.values_list('city', flat=True).distinct().order_by('city')
    result_list = [[country, country] for country in cities_list]

    return result_list


class EquipmentFilter(django_filters.FilterSet):
    name = CharFilter(
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}),
        label='Mark',
        lookup_expr='icontains'
    )
    manufacture = ModelChoiceFilter(
        queryset=Manufacture.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control mb-3'})
    )
    type = ChoiceFilter(
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        label='Equipment Type',
        choices=EQUIPMENT_TYPES
    )
    created_at = DateFromToRangeFilter(
        widget=RangeWidget(attrs={
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control mb-3'
        }),
        label='Created'
    )
    position__technological_node__location__country = ChoiceFilter(
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=get_countries(),
        label='Country'
    )
    position__technological_node__location__city = ChoiceFilter(
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=get_cities(),
        label='City'
    )
    order_by = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('manufacture__name', 'manufacture__name'),
            ('type', 'type'),
            ('power', 'power'),
            ('weight', 'weight'),
        ),
        field_labels={
            'created_at': 'Created date',
            'name': 'Mark',
            'manufacture__name': 'Manufacture',
            'type': 'Equipment type',
            'power': 'Power',
            'weight': 'Weight',
        },
        label='Order by',
    )

    class Meta:
        model = Equipment
        fields = [
            'name',
            'manufacture',
            'type',
            'position__technological_node__location__country',
            'position__technological_node__location__city',
            'created_at',
            ]


class EquipmentStatisticFilter(django_filters.FilterSet):
    avg_price = NumericRangeFilter(
        widget=RangeWidget(attrs={
            'class': 'form-control mb-3'
        }),
        label='Average price',
        method='filter_avg_price'

    )
    order_by = django_filters.OrderingFilter(
        fields=(
            ('type', 'type'),
            ('count', 'count'),
            ('avg_price', 'avg_price'),
            ('max_price', 'max_price'),
            ('min_price', 'type'),
            ('quantity', 'quantity'),
            ('projects', 'weight'),
        ),
        field_labels={
            'type': 'Equipment type',
            'count': 'Types quantity',
            'avg_price': 'Average price',
            'max_price': 'Max price',
            'min_price': 'Min price',
            'quantity': 'Equipment quantity',
            'projects': 'Project',
        },
        label='Order by',
    )

    class Meta:
        model = Equipment
        fields = ['avg_price', ]

    def filter_avg_price(self, queryset, name, value):
        if value.start is not None or value.stop is not None:
            start = value.start if value.start else 0
            stop = value.stop if value.stop else 10000000
            queryset = queryset.annotate(avg_price=Avg('price')).filter(avg_price__range=[start, stop])
        return queryset
