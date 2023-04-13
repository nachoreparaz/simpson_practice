from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scrapper.views import EpisodeViewSet

# episode_list = EpisodeViewSet.as_view({"get": "list", "post": "create"})
# episode_random = EpisodeViewSet.as_view({"get": "get_random_episode"})

router = DefaultRouter()
router.register(r"episodes", EpisodeViewSet, basename="episode")
router.register(r"episodes/random", EpisodeViewSet, basename="random-episode")

urlpatterns = [
    path("", include(router.urls)),
]
