from django.shortcuts import get_object_or_404
from rest_framework import serializers

from feedback.models import FeedbackModel
from feedback.serializers import BasicListFeedbackSerializer
from shared.serializers import BasicListUserSerializer
from user.models import User
from .models import TimelineModel


class ListTimelineSerializer(serializers.ModelSerializer):
    """ Returns a serialized list of App TimelineModel """

    class Meta:
        model = TimelineModel
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["app"] = BasicListFeedbackSerializer(instance=get_object_or_404(FeedbackModel, pk=instance.app)).data
        data["user"] = BasicListUserSerializer(instance=get_object_or_404(User, pk=instance.get("owner"))).data
        return data
