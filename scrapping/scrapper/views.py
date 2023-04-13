from django.shortcuts import render
from scrapper.models import Episode
from scrapper.serializer import EpisodeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
import random


# Create your views here.


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
        random_episode = random.choice(self.queryset)
        serializer = EpisodeSerializer(random_episode)
        return Response(serializer.data)

    def create_or_update_episode(self, request, instance=None):
        serializer = self.serializer_class(
            instance=instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        name = request.data.get("name")
        existing_episodes = Episode.objects.filter(name=name)
        if existing_episodes.exists():
            return self.create_or_update_episode(request, instance=existing_episodes[0])
        return self.create_or_update_episode(request)

    def filter_queryset(self, queryset):
        season = self.request.query_params.get("season")
        if season is not None and len(season) > 0:
            queryset = queryset.filter(season_number__in=season.split(","))

        return queryset

    def retrieve(self, request, pk=None):
        episode = self.get_object()
        serializer = self.serializer_class(episode)
        return Response(serializer.data)
