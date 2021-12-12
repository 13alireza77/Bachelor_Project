import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from crawl.divar.post import CrawlPost
from crawl.formatter import PostFormater
from user_api.api.serializers import UserSerializer, AccessLevelSerializer, RequestSerializer, SuggestionsSerializer
from user_api.celery_task import render_xlsx_from_mongo
from user_api.models import AccessLevel


@extend_schema_view(
    post=extend_schema(tags=[_("register")], summary=_("create account")),
)
class UserCreateViewSet(generics.CreateAPIView, viewsets.ViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


@extend_schema_view(
    post=extend_schema(tags=[_("accessleve")], summary=_("create access leve")),
)
class AccessLevelViewSet(generics.CreateAPIView, viewsets.ViewSet):
    queryset = AccessLevel.objects.all()
    serializer_class = AccessLevelSerializer
    permission_classes = (IsAdminUser,)


@extend_schema_view(
    request_suggestions=extend_schema(tags=[_("suggestions")], summary=_("get suggestions of token")),
    get_request_suggestions_xlsx=extend_schema(tags=[_("suggestions")], summary=(_("get suggestions xlsx")),
                                               parameters=[
                                                   OpenApiParameter("request_id", OpenApiTypes.STR, required=True), ])
)
class RequestViewSet(GenericViewSet):
    queryset = AccessLevel.objects.all()
    permission_classes = (IsAuthenticated,)
    crawl_post = CrawlPost()
    static_suggestions = "resources/static/suggestions"
    static_data = "resources/static/data"

    def get_serializer_class(self):
        if self.action == 'request_suggestions':
            return SuggestionsSerializer
        else:
            return RequestSerializer

    @action(methods=['post'], detail=False)
    def request_xlsx(self, *args, **kwargs):
        pass

    @action(methods=['post'], detail=False)
    def request_suggestions(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        try:
            access_level = self.get_queryset().get(user=self.request.user)
        except Exception:
            return Response("No access level defined for this user")
        status, response = self.crawl_post.get_post(token)
        if status != 1:
            return Response(f"{token} expired or is wrong")
        try:
            json_data = PostFormater(response).clean()["suggestions"][:3]
        except Exception:
            return Response("cant get suggestions")
        request_id = str(uuid.uuid4())
        access_level.update_max_number_of_data(len(json_data))
        render_xlsx_from_mongo(request_id=request_id, static_path=self.static_suggestions, suggestions=json_data)
        return Response(request_id)

    @action(methods=['get'], detail=False)
    def get_request_suggestions_xlsx(self, *args, **kwargs):
        query_params = self.request.query_params
        request_id = query_params.get('request_id')
        fs = FileSystemStorage(
            base_url="/static/",
            location=settings.STATICFILES_DIRS[0]
        )
        if fs.exists(f"suggestions/{request_id}.xlsx"):
            return HttpResponse(fs.open(f"suggestions/{request_id}.xlsx"),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                headers={"Content-Disposition": f"attachment; filename={request_id}.xlsx"})
        else:
            return Response("not exist")
