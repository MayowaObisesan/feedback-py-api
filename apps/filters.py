import django_filters

from apps.models import AppsModel, VersionModel


class AppsFilters(django_filters.FilterSet):
    """ Filters for Nine Apps """
    name = django_filters.CharFilter(field_name='name', lookup_expr='iexact')

    class Meta:
        model = AppsModel
        fields = ["name", "name_id", "category"]


class VersionFilters(django_filters.FilterSet):
    """ Filters for Nine VersionModel """
    class Meta:
        model = VersionModel
        fields = ["app", "release_type", "is_upgrade"]
