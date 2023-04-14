from scrapper.models import Episode
from rest_framework import serializers
from datetime import datetime
from django.utils.translation import gettext


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
