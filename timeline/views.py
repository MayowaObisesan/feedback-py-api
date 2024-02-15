from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework_simplejwt.authentication import JWTAuthentication

from timeline.filters import TimelineFilters
from timeline.models import TimelineModel
from timeline.serializers import ListTimelineSerializer


class TimelineView(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineModel.objects.all()
    serializer_class = ListTimelineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    # pagination_class = NinePagination
    filterset_class = TimelineFilters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['entity', 'category']
