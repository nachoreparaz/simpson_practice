from scrapper.models import Episode
from django.contrib.auth.models import User
from scrapper.serializer import EpisodeSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

import random


class EpisodesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ["create", "retrieve", "update", "destroy", "partial_update"]:
            return request.user and request.user.is_authenticated

        return True


class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    pagination_class = EpisodesPagination
    permission_classes = [CustomPermission]

    def check_permission(self, request, instance):
        if not request.user.is_authenticated:
            return False

        if not request.user.has_perm("scrapper.EpisodeViewSet", instance):
            return False

        breakpoint()
        return True

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
        print("Esta es la lista de usuarios")
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

    def retrieve(self, request):
        instance = self.get_object()
        if not self.check_permission(request, instance):
            return Response(status=status.HTTP_403_FORBIDDEN)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        users_queryset = self.queryset
        if len(users_queryset) > 0:
            user_serialize = self.serializer_class(users_queryset, many=True)
            return Response(user_serialize.data)
        return Response([])

    def create(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainPairSerializerWithEmail(TokenObtainPairSerializer):
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class ObtainTokenPairWithEmailView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializerWithEmail
