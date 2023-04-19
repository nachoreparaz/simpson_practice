from scrapper.models import Episode
from rest_framework import serializers
from datetime import datetime
from django.utils.translation import gettext
from django.contrib.auth.models import User


class CustomizeDateField(serializers.Field):
    def to_representation(self, value):
        return value.strftime("%Y-%d-%m")

    def to_internal_value(self, data):
        try:
            release_date = datetime.strptime(data, "%Y-%d-%m")
        except ValueError:
            error_output_translate = gettext(
                "La fecha debe estar en formato yyyy-dd-mm"
            )
            raise serializers.ValidationError(error_output_translate)
        return release_date


class EpisodeSerializer(serializers.ModelSerializer):
    release_date = CustomizeDateField()

    class Meta:
        model = Episode
        fields = "__all__"


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"], email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
