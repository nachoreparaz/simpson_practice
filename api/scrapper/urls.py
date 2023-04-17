from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scrapper.views import EpisodeViewSet

router = DefaultRouter()
router.register(r"episodes", EpisodeViewSet, basename="episode")

urlpatterns = [
    path("", include(router.urls)),
]
