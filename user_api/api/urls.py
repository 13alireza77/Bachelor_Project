from rest_framework import routers

from django.urls import path, include

from .views import CcsActivityViewSet

router = routers.DefaultRouter(trailing_slash=True)

router.register(r'', CcsActivityViewSet, basename='activity')

urlpatterns = [
    path('activity/', include(router.urls)),
]
