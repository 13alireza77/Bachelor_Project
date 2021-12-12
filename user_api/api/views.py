from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from user_api.api.serializers import UserSerializer


@extend_schema_view(
    get=extend_schema(tags=[_("activity")], summary=_("list of activity")),
)
class CcsActivityViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['POST'])
    def get(self, *args, **kwargs):
        return Response("hi")


@extend_schema_view(
    post=extend_schema(tags=[_("register")], summary=_("create account")),
)
class UserCreateViewSet(generics.CreateAPIView, viewsets.ViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
