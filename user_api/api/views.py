from django.utils.translation import ugettext_lazy as _
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny


@extend_schema_view(
    get=extend_schema(tags=[_("activity")], summary=_("list of activity")),
)
class CcsActivityViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def get(self):
        return "hi"
