import base64
import uuid

import six
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from shared.serializers import BasicListUserSerializer
from .models import FeedbackModel, ImageModel
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


class FeedbackSearchSerializer(serializers.ModelSerializer):
    """
    This Serializer is for Feedback Search. It only performs validation on the app_name fields.
    """

    class Meta:
        model = FeedbackModel
        fields = ["title", "description", "long_description", "category"]


class FeedbackImageSerializer(serializers.ModelSerializer):
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


class BasicListFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackModel
        fields = "__all__"


class ListFeedbackSerializer(serializers.ModelSerializer):
    """ Returns a serialized list of Feedback """
    class Meta:
        model = FeedbackModel
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["owner"] = BasicListUserSerializer(instance=get_object_or_404(User, pk=instance.owner)).data
        data["screenshot"] = FeedbackImageSerializer(instance=instance.screenshot, many=True, context={"request": self.context.get("request")}).data
        return data


class FeedbackSerializer(serializers.ModelSerializer):
    """
    # HyperlinkedModelSerializer has the following differences from ModelSerializer:
    # a. It does not include the id field by default.
    # b. It includes a url field, using HyperlinkedIdentityField.
    # c. Relationships use HyperlinkedRelatedField instead of PrimaryKeyRelatedField.
    """

    # The source argument controls which attribute is used to populate a field,
    # and can point at any attribute on the serialized instance.
    # app_owner = serializers.ReadOnlyField(source="app_owner.username")
    # app_bio = serializers.HyperlinkedIdentityField(view_name="feedback-bio", format="html")
    # or app_owner = serializers.CharField(read_only=True)

    # url = serializers.SerializerMethodField(read_only=True)

    screenshot = serializers.ListField(
        child=serializers.ImageField(), required=False
    )

    class Meta:
        model = FeedbackModel
        fields = [
            "id", "owner", "external_link", "category", "website",
            "title", "description", "long_description", "screenshot"
        ]
        read_only_fields = ["owner"]
        extra_kwargs = {
            "screenshot": {"required": False, "allow_null": True}
        }

    # def get_url(self, obj):
    #     request = self.context.get('request')
    #     if request is None:
    #         return None
    #     return reverse("feedback-detail", kwargs={'pk': obj.pk}, request=request)

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
        new_feedback = self.Meta.model.objects.create(**validated_data)
        screenshot_list: list = list()
        for each_screenshot in screenshots:
            screenshot_list.append(ImageModel.objects.create(image=each_screenshot))
        new_feedback.screenshot.set(screenshot_list)
        return validated_data

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance.external_link = validated_data.get("external_link", instance.external_link)
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.long_description = validated_data.get("long_description", instance.long_description)
        instance.category = validated_data.get("category", instance.category)
        instance.website = validated_data.get("website", instance.website)
        if screenshots := request.FILES.getlist("screenshots"):
            for each_screenshot in screenshots:
                instance.screenshot.add(ImageModel.objects.create(image=each_screenshot))
            validated_data["screenshots"] = instance.screenshot.all()
        instance.save()
        validated_data.update(**self.Meta.model.objects.filter(pk=instance.pk).values()[0])
        return validated_data
