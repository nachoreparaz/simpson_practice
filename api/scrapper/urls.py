from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scrapper.views import EpisodeViewSet, UserViewSet, ObtainTokenPairWithEmailView

router = DefaultRouter()
router.register(r"episodes", EpisodeViewSet, basename="episode")
router.register(r"auth", UserViewSet, basename="user")
urlpatterns = [
    path(
        "api/token/", ObtainTokenPairWithEmailView.as_view(), name="token_obtain_pair"
    ),
]
urlpatterns += router.urls
