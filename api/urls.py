from django.urls import path, include
from rest_framework import routers
from .views import AudioFileListView

router = routers.DefaultRouter()
router.register(r"audiofile", AudioFileListView)


urlpatterns = [
    path("", include(router.urls)),
]