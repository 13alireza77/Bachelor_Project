import logging
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
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
from user_api.api.serializers import UserSerializer, AccessLevelSerializer, SuggestionsSerializer, \
    DatasSerializer
from user_api.models import AccessLevel, RequestHistory
from user_api.tasks import render_suggestions_xlsx, render_datas_xlsx


class SuggestionsResponse(Response):
    def __init__(self, json_data, request_id, static_suggestions, types, data=None, status=None,
                 template_name=None,
                 headers=None, exception=False,
                 content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        self.request_id = request_id
        self.json_data = json_data
        self.static_suggestions = static_suggestions
        self.types = types

    def close(self):
        super(SuggestionsResponse, self).close()
        try:
            render_suggestions_xlsx(request_id=self.request_id, static_path=self.static_suggestions,
                                    suggestions=self.json_data, types=self.types)
        except Exception as e:
            request_history = RequestHistory.objects.get(request_id=self.request_id)
            request_history.status = 0
            request_history.save()
            logging.error(e)


class DatasResponse(Response):
    def __init__(self, request_id, static_datas, types, from_date, to_date, page: int, page_count: int, user,
                 categories=None,
                 city=None,
                 title=None, data=None, status=None,
                 template_name=None, headers=None, exception=False, content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        self.request_id = request_id
        self.static_datas = static_datas
        self.types = types
        self.from_date = from_date
        self.to_date = to_date
        self.categories = categories
        self.city = city
        self.title = title
        self.page = page
        self.page_count = page_count
        self.user = user

    def close(self):
        super(DatasResponse, self).close()
        try:
            render_datas_xlsx(request_id=self.request_id, static_path=self.static_datas, from_date=self.from_date,
                              to_date=self.to_date, categories=self.categories, city=self.city, title=self.title,
                              types=self.types, page=self.page, page_count=self.page_count, user=self.user)
        except Exception as e:
            request_history = RequestHistory.objects.get(request_id=self.request_id)
            request_history.status = 0
            request_history.save()
            logging.error(e)


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
                                                   OpenApiParameter("request_id", OpenApiTypes.STR, required=True), ]),

    request_datas_xlsx=extend_schema(tags=[_("datas")], summary=_("get datas")),
    get_request_datas_xlsx=extend_schema(tags=[_("datas")], summary=(_("get datas xlsx")),
                                         parameters=[
                                             OpenApiParameter("request_id", OpenApiTypes.STR, required=True), ])

)
class RequestViewSet(GenericViewSet):
    queryset = AccessLevel.objects.all()
    permission_classes = (IsAuthenticated,)
    crawl_post = CrawlPost()
    static_suggestions = "resources/static/suggestions"
    static_data = "resources/static/data"
    max_suggestions_count = 20
    page_count = 500

    def get_serializer_class(self):
        if self.action == 'request_suggestions':
            return SuggestionsSerializer
        else:
            return DatasSerializer

    @action(methods=['post'], detail=False)
    def request_datas_xlsx(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        from_date = serializer.validated_data["from_date"]
        to_date = serializer.validated_data["to_date"]
        page = serializer.validated_data["page"]
        categories = serializer.validated_data.get("categories")
        city = serializer.validated_data.get("city")
        title = serializer.validated_data.get("title")
        types = serializer.validated_data.get("type")
        if types is None:
            types = "data"
        request_id = str(uuid.uuid4())
        RequestHistory.create_request_history(user=self.request.user, request_id=request_id)
        return DatasResponse(data=request_id, request_id=request_id, static_datas=self.static_data, types=types,
                             from_date=from_date, to_date=to_date, categories=categories, city=city, title=title,
                             page=page, page_count=self.page_count, user=self.request.user)

    @action(methods=['get'], detail=False)
    def get_request_datas_xlsx(self, *args, **kwargs):
        query_params = self.request.query_params
        request_id = query_params.get('request_id')
        fs = FileSystemStorage(
            base_url="/static/",
            location=settings.STATICFILES_DIRS[0]
        )
        if fs.exists(f"datas/{request_id}.xlsx"):
            return HttpResponse(fs.open(f"datas/{request_id}.xlsx"),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                headers={"Content-Disposition": f"attachment; filename={request_id}.xlsx"})
        else:
            try:
                status = RequestHistory.objects.get(request_id=request_id).status
                if status:
                    return Response("sth went wrong, request for get datas again")
                return Response("process of getting datas not finished")
            except:
                return Response("invalid request_id")

    @action(methods=['post'], detail=False)
    def request_suggestions(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        types = serializer.validated_data.get("type")
        if types is None:
            types = "data"
        try:
            access_level = self.get_queryset().get(user=self.request.user)
        except Exception:
            return Response("No access level defined for this user")
        if access_level.max_number_of_data and access_level.max_number_of_data < 1:
            return Response(f"The number of your requests has been completed")
        status, response = self.crawl_post.get_post(token)
        if status != 1:
            return Response(f"{token} expired or is wrong")
        try:
            json_data = PostFormater(response).clean()["suggestions"][:self.max_suggestions_count]
        except Exception:
            return Response("cant get suggestions")
        request_id = str(uuid.uuid4())
        RequestHistory.create_request_history(user=self.request.user, request_id=request_id,
                                              count_data=self.max_suggestions_count)
        access_level.update_max_number_of_data(len(json_data))
        return SuggestionsResponse(data=request_id, request_id=request_id, json_data=json_data,
                                   static_suggestions=self.static_suggestions, types=types)

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
            try:
                status = RequestHistory.objects.get(request_id=request_id).status
                if status:
                    return Response("sth went wrong, request for get suggestions again")
                return Response("process of getting suggestions not finished")
            except:
                return Response("invalid request_id")
