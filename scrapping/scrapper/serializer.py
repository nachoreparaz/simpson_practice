from scrapper.models import Episode
from rest_framework import serializers
from datetime import datetime


class FechaPersonalizada(serializers.Field):
    def to_representation(self, value):
        return value.strftime("%Y-%d-%m")

    def to_internal_value(self, data):
        try:
            release_date = datetime.strptime(data, "%Y-%d-%m")
        except ValueError:
            raise serializers.ValidationError(
                "La fecha debe estar en formato yyyy-dd-mm"
            )
        return release_date


class EpisodeSerializer(serializers.ModelSerializer):
    release_date = FechaPersonalizada()

    class Meta:
        model = Episode
        fields = "__all__"
