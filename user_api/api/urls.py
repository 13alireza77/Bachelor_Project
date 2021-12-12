from django.urls import path, include
from rest_framework import routers

from .views import CcsActivityViewSet, UserCreateViewSet

router = routers.DefaultRouter(trailing_slash=True)
router.register(r'', CcsActivityViewSet, basename='activity')
router.register(r'account/register', UserCreateViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
]
