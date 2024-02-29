from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_list_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .enums import APPLE_APPS_CATEGORY
from .filters import FeedbackFilters
from .models import FeedbackModel, ImageModel, TimelineModel
from .pagination import NinePagination
from .permissions import IsAppCreatorOrReadOnly
from .serializers import (
    FeedbackSerializer,
    FeedbackSearchSerializer,
    ListFeedbackSerializer,
    FeedbackImageSerializer
)
from .enums import SOCIAL_ACCOUNT_CHOICES


class SearchView(viewsets.ModelViewSet):
    queryset = FeedbackModel.objects.all()
    serializer_class = FeedbackSearchSerializer

    def get_queryset(self):
        return FeedbackModel.objects.all()


class FeedbackView(viewsets.ModelViewSet):
    queryset = FeedbackModel.objects.all()
    serializer_class = ListFeedbackSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    # pagination_class = NinePagination
    filterset_class = FeedbackFilters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    http_method_names = ["get", "post", "patch", "put", "delete"]
    # parser_classes = []
    # lookup_field = 'name_id'
    # lookup_url_kwarg = 'name'
    search_fields = ['description', 'long_description']
    # ordering_fields = ['name']

    def get_object(self):
        obj = super().get_object()
        return obj

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FeedbackSerializer
        return self.serializer_class

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [permissions.IsAuthenticated, IsAppCreatorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_authenticators(self):
        authentication_classes = self.authentication_classes
        # print(f"ACTION: +++{self.action}")
        try:
            if self.request.POST:
                print("INside write requests")
                authentication_classes = [JWTAuthentication]
            if self.request.GET:
                authentication_classes = []
        except:
            pass
        return [authenticator() for authenticator in authentication_classes]

    def get_serializer_context(self):
        default_context = super().get_serializer_context()
        # formatted_uuids = [str(_) for _ in self.queryset.values_list('approved_by', flat=True) if _]
        # approver_list = get_users_by_id(self.request, formatted_uuids)
        # default_context['approver_list'] = approver_list
        default_context['request'] = self.request
        return default_context

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.serializer_class(instance, data=request.data, partial=True)
    #     print("Inside update method")
    #     serializer.is_valid(raise_exception=True)
    #     # serialized_data = serializer.validated_data
    #     # instance.save()
    #     serializer.save()
    #     return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name", OpenApiTypes.STR, OpenApiParameter.QUERY, required=True
            ),
        ],
        methods=["GET"]
    )
    @action(methods=["GET"], detail=False, url_path="exists")
    def name_exists(self, request):
        """ Endpoint that returns if an app name exist """
        app_name: str = request.query_params.get("name", "")
        if app_name:
            app_name = app_name.strip().lower()
        exists = self.queryset.filter(name__iexact=app_name).exists()
        return Response(data={"exists": exists}, status=status.HTTP_200_OK)


    # @action(methods=["GET", "POST"], detail=False, url_path="search", permission_classes=[],
    #         serializer_class=AppsSearchSerializer)
    def search_apps(self, request, pk=None):
        app_obj = FeedbackModel.objects.all()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_name = serializer.validated_data.get('app_name')
        print(f"APP NAME FROM SERIALIZER VALIDATED DATA is: {app_name}")

        if request.method == "GET":
            app_search_obj = get_list_or_404(app_obj, **serializer.validated_data)
            app_serializer = self.serializer_class(app_search_obj, many=True, data=request.data)
            return Response(app_serializer.data)
        elif request.method == "POST":
            app_search_obj = FeedbackModel.objects.filter(
                Q(app_name__icontains=app_name)
                | Q(app_owner__username__icontains=app_name)
            )
            app_search_serializer = self.serializer_class(app_search_obj, many=True, data=request.data)
            app_search_serializer.is_valid(raise_exception=True)
            search_serializer = FeedbackSerializer(app_search_obj, many=True)
            return Response(search_serializer.data)

        # search_query_params = request.query_params
        # print(f"SEARCH QUERY PARAMS: {search_query_params}")
        # print(f"SEARCH QUERY PARAMS: {serializer.validated_data}")
        # # Instead of using request.query_params, use serializer.validated_data.
        #
        # if request.method == "GET":
        #     query_dict = {}
        #     for each_search_key, each_search_value in search_query_params.items():
        #         query_dict[each_search_key] = each_search_value
        #     print(f"SEARCH QUERY IS: {search_query_params}")
        #     print(f"SEARCH QUERY CUSTOM DICT IS: {query_dict}")
        #     app_search_obj = get_object_or_404(app_obj, **query_dict)
        #     print(app_search_obj)
        #     app_serializer = self.serializer_class(app_search_obj)
        #     return Response(app_serializer.data)
        # elif request.method == "POST":
        #     app_name_query = request.data.get("app_name")
        #     # print(f"App Name Search String: {app_name_query}")
        #     # print(f"Request params: {dir(request)}")
        #     search_filter_obj = AppsModel.objects.filter(Q(app_name__icontains=app_name_query) |
        #                                                  Q(app_owner__username__icontains=app_name_query))
        #     print(f"SEARCH FILTER OBJ: {search_filter_obj}")
        #     # search_result_serializer = AppsSearchSerializer()
        #     search_result_serializer = AppsSerializer(
        #         search_filter_obj, many=True, data=request.data
        #     )
        #     if search_result_serializer.is_valid():
        #         return Response(
        #             search_result_serializer.data
        #         )
        #     return Response(search_result_serializer.errors)

    @action(methods=["GET"], detail=False, url_path="latest", serializer_class=FeedbackSerializer, authentication_classes=[])
    def latest_apps(self, request, pk=None):
        apps_obj = self.queryset.filter(created_at__range=[timezone.now(), timezone.now()+timezone.timedelta(days=50)])
        app_serializer = self.serializer_class(apps_obj, many=True)
        # app_serializer.is_valid(raise_exception=True)
        return Response(app_serializer.data)

    @action(methods=["GET"], detail=False, url_path="social_list")
    def social_list(self, request):
        """ The endpoint to list the social sites available on Nine. """
        return Response(dict(SOCIAL_ACCOUNT_CHOICES).values(), status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path="category_list")
    def category_list(self, request):
        """ The endpoint to list the category sites available on Nine. """
        return Response(dict(APPLE_APPS_CATEGORY).values(), status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, url_path=r"screenshot/(?P<id>[^/.]+)")
    def get_screenshot(self, request, id):
        """
         Endpoint to get a screenshot.
        :param request: The HTTPRequest
        :param id: The id of the screenshot image
        :return: A JSON response of the screenshot
        """
        image_obj = ImageModel.objects.filter(pk=id)
        if not image_obj.exists():
            return Response(data={"success": False}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedbackImageSerializer(image_obj.first())
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(methods=["PATCH"], detail=False, url_path=r"screenshot/(?P<id>[^/.]+)/update")
    def update_screenshot(self, request, id):
        """
         Endpoint to update a screenshot.
        :param request: The HTTPRequest
        :param id: The id of the screenshot image
        :return: A JSON response of the screenshot
        """
        image_obj = ImageModel.objects.filter(pk=id)
        if not image_obj.exists():
            return Response(data={"success": False}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedbackImageSerializer(image_obj.first(), data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=["DELETE"], detail=False, url_path=r"screenshot/(?P<id>[^/.]+)/delete")
    def delete_screenshot(self, request, id):
        """
        Endpoint to delete a screenshot before adding a new one.
        :param request: The HTTPRequest
        :param id: The id of the screenshot image
        :return: A JSON response of true or false
        """
        image_obj = ImageModel.objects.filter(pk=id)
        if not image_obj.exists():
            return Response(data={"success": False}, status=status.HTTP_404_NOT_FOUND)
        image_obj.delete()
        return Response(data={"success": True}, status=status.HTTP_200_OK)
