import django_filters

from feedback.models import FeedbackModel


class FeedbackFilters(django_filters.FilterSet):
    """ Filters for Nine Apps """
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')

    class Meta:
        model = FeedbackModel
        fields = ["category"]
