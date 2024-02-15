import django_filters

from timeline.models import TimelineModel


class TimelineFilters(django_filters.FilterSet):
    """ Filters for Nine Timeline """
    entity = django_filters.CharFilter(field_name='entity', lookup_expr='iexact')

    class Meta:
        model = TimelineModel
        fields = ["user", "app", "entity", "category"]
