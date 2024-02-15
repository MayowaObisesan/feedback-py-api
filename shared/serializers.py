from rest_framework import serializers

from user.models import User


class BasicListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "dp", "email", "phone_no", "firstname", "lastname", "address",
            "country", "is_verified", "date_joined", "is_registered"
        )


class BrandUserSerializer(serializers.ModelSerializer):
    """ Define the representation of Brands. """

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }
