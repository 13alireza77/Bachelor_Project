from django.urls import path, include
from rest_framework import routers

from .views import UserCreateViewSet, AccessLevelViewSet, RequestViewSet

router = routers.DefaultRouter(trailing_slash=True)
router.register(r'account/register', UserCreateViewSet, basename='register')
router.register(r'accesslevel', AccessLevelViewSet, basename='accesslevel')
router.register(r'requests', RequestViewSet, basename='requests')

urlpatterns = [
    path('', include(router.urls)),
]
