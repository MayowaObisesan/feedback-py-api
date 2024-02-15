import base64
import uuid

import six
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from shared.serializers import BasicListUserSerializer
from .models import AppsModel, ImageModel, VersionModel
from timeline.models import TimelineModel
from user.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')
            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except:
                # except TypeError:
                self.fail('invalid_image')
            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension,)
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


class AppsSearchSerializer(serializers.ModelSerializer):
    """
    This Serializer is for Apps Search. It only performs validation on the app_name fields.
    """

    class Meta:
        model = AppsModel
        fields = ["name"]


class AppImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ["id", "image"]
    #
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     request = self.context.get("request")
    #     # data["image"] = request.META.get("HTTP_REFERER").split(":")[0]+"://"+request.get_host()+instance.image.url
    #     return data

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        print(validated_data.get('screenshots'))
        print(request.FILES.getlist("screenshots"))
        if screenshots := request.FILES.getlist("screenshots"):
            for each_screenshot in screenshots:
                instance.image = each_screenshot
        instance.save()
        return instance


class BasicListAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppsModel
        fields = "__all__"

class ListAppsSerializer(serializers.ModelSerializer):
    """ Returns a serialized list of Apps """
    class Meta:
        model = AppsModel
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["owner"] = BasicListUserSerializer(instance=get_object_or_404(User, pk=instance.owner)).data
        data["screenshot"] = AppImageSerializer(instance=instance.screenshot, many=True, context={"request": self.context.get("request")}).data
        data["current_version"] = VersionSerializer(instance=VersionModel.objects.last()).data
        return data


class AppsSerializer(serializers.ModelSerializer):
    """
    # HyperlinkedModelSerializer has the following differences from ModelSerializer:
    # a. It does not include the id field by default.
    # b. It includes a url field, using HyperlinkedIdentityField.
    # c. Relationships use HyperlinkedRelatedField instead of PrimaryKeyRelatedField.
    """

    # The source argument controls which attribute is used to populate a field,
    # and can point at any attribute on the serialized instance.
    # app_owner = serializers.ReadOnlyField(source="app_owner.username")
    # app_bio = serializers.HyperlinkedIdentityField(view_name="apps-bio", format="html")
    # or app_owner = serializers.CharField(read_only=True)

    # url = serializers.SerializerMethodField(read_only=True)

    screenshot = serializers.ListField(
        child=serializers.ImageField(), required=False
    )

    class Meta:
        model = AppsModel
        fields = [
            "id", "name", "name_id", "logo", "owner", "playstore_link", "appstore_link",
            "external_link", "category", "version", "website", "description", "details", "screenshot",
            # "bio",
        ]
        read_only_fields = ["owner", "name_id"]
        extra_kwargs = {
            "screenshot": {"required": False, "allow_null": True}
        }

    # def get_url(self, obj):
    #     request = self.context.get('request')
    #     if request is None:
    #         return None
    #     return reverse("apps-detail", kwargs={'pk': obj.pk}, request=request)

    def to_representation(self, instance):
        """
        define the way the api will be presented.
        :param instance: The model on which to_representation is being overriden. i.e., self.Meta.model
        :return: a dict response / The data of the serialized model.
        """
        data = super().to_representation(instance)
        # brand_obj = BrandUserSerializer(instance=instance.owner).data
        # data['owner'] = brand_obj
        # print(instance)
        data["owner"] = BasicListUserSerializer(instance=get_object_or_404(User, pk=instance.get("owner"))).data
        # data["screenshot"] = AppImageSerializer(instance=instance.screenshot, many=True).data
        return data

    @transaction.atomic
    def create(self, validated_data):

        request = self.context.get("request")
        # screenshots_list = request.FILES.getlist("screenshots")
        # print(screenshots_list)
        # print(validated_data)
        screenshots = validated_data.pop("screenshot", [])
        print(screenshots)
        # Strip excess "," from category
        if validated_data["category"]:
            # validated_data["category"] = validated_data["category"][:-1]
            validated_data["category"] = validated_data["category"].lstrip(',')
        validated_data["owner"] = request.user.id
        # validated_data["name_id"] = self.generate_name_id(validated_data.get("name"))
        new_app = self.Meta.model.objects.create(**validated_data)
        screenshot_list: list = list()
        for each_screenshot in screenshots:
            screenshot_list.append(ImageModel.objects.create(image=each_screenshot))
        new_app.screenshot.set(screenshot_list)
        return validated_data

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.logo = validated_data.get("logo", instance.logo)
        instance.name = validated_data.get("name", instance.name)
        # instance.name_id = self.generate_name_id(instance.name)
        instance.playstore_link = validated_data.get("playstore_link", instance.playstore_link)
        instance.appstore_link = validated_data.get("appstore_link", instance.appstore_link)
        instance.external_link = validated_data.get("external_link", instance.external_link)
        instance.description = validated_data.get("description", instance.description)
        instance.category = validated_data.get("category", instance.category)
        instance.stack = validated_data.get("stack", instance.stack)
        instance.version = validated_data.get("version", instance.version)
        instance.website = validated_data.get("website", instance.website)
        instance.details = validated_data.get("details", instance.details)
        instance.bio = validated_data.get("bio", instance.bio)
        if screenshots := request.FILES.getlist("screenshots"):
            for each_screenshot in screenshots:
                instance.screenshot.add(ImageModel.objects.create(image=each_screenshot))
            validated_data["screenshots"] = instance.screenshot.all()
        instance.save()
        validated_data.update(**self.Meta.model.objects.filter(pk=instance.pk).values()[0])
        return validated_data


class ListVersionSerializer(serializers.ModelSerializer):
    """ Returns a serialized list of App VersionModel """
    class Meta:
        model = VersionModel
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["app"] = BasicListAppsSerializer(instance=get_object_or_404(AppsModel, pk=instance.app)).data
        return data


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionModel
        fields = "__all__"

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        VersionModel.objects.create(**validated_data)
        # Create the timeline for the new app version
        TimelineModel.objects.create_app_timeline(
            user_id=request.user.id, app_id=validated_data.get("app"), category="NEW_VERSION"
        )
        return validated_data
