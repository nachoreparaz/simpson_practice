from scrapper.models import Episode
from scrapper.serializer import EpisodeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError

import random


class EpisodesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    pagination_class = EpisodesPagination

    @action(detail=False, methods=["GET"])
    def random(self, request):
        filter_episode_queryset = self.filter_queryset(self.queryset)
        if filter_episode_queryset.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        random_episode = random.choice(filter_episode_queryset)
        serializer = EpisodeSerializer(random_episode)
        return Response(serializer.data)

    def list(self, request):
        episodes_per_season = request.query_params.get("season", None)
        if not episodes_per_season:
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            return Response(serializer.data)

        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() == 0:
            return Response([], status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def _upsert(self, request, instance=None):
        serializer = self.get_serializer(
            instance=instance, data=request.data, partial=instance is not None
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        name = request.data.get("name")
        existing_episodes = Episode.objects.filter(name=name)
        if existing_episodes.exists():
            return self._upsert(request, instance=existing_episodes[0])
        return self._upsert(request)

    def filter_queryset(self, queryset):
        season = self.request.query_params.get("season")
        if season is not None and len(season) > 0:
            queryset = queryset.filter(season_number__in=season.split(","))

        return queryset

    def retrieve(self, request, pk=None):
        episode = self.get_object()
        serializer = self.serializer_class(episode)
        return Response(serializer.data)
