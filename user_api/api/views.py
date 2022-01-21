import io
import json
import logging
import uuid

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from crawl.divar.post import CrawlPost
from crawl.formatter import PostFormater
from user_api.api.serializers import UserSerializer, AccessLevelSerializer, SuggestionsSerializer, \
    DatasSerializer
from user_api.models import AccessLevel, RequestHistory
from user_api.tasks import render_suggestions_xlsx, render_datas


class SuggestionsResponse(Response):
    def __init__(self, json_data, request_id, static_suggestions, data=None, status=None,
                 template_name=None,
                 headers=None, exception=False,
                 content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        self.request_id = request_id
        self.json_data = json_data
        self.static_suggestions = static_suggestions

    def close(self):
        super(SuggestionsResponse, self).close()
        try:
            render_suggestions_xlsx(request_id=self.request_id, static_path=self.static_suggestions,
                                    suggestions=self.json_data)
        except Exception as e:
            request_history = RequestHistory.objects.get(request_id=self.request_id)
            request_history.status = 0
            request_history.save()
            logging.error(e)


class DatasResponse(Response):
    def __init__(self, request_id, static_datas, from_date, to_date, page: int, page_count: int, user,
                 categories=None,
                 city=None,
                 title=None, data=None, status=None,
                 template_name=None, headers=None, exception=False, content_type=None):
        super().__init__(data, status, template_name, headers, exception, content_type)
        self.request_id = request_id
        self.static_datas = static_datas
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
            render_datas(request_id=self.request_id, static_path=self.static_datas, from_date=self.from_date,
                         to_date=self.to_date, categories=self.categories, city=self.city, title=self.title,
                         page=self.page, page_count=self.page_count, user=self.user)
        except Exception as e:
            request_history = RequestHistory.objects.get(request_id=self.request_id)
            request_history.status = 0
            request_history.save()
            logging.error(e)


@extend_schema_view(
    post=extend_schema(tags=[_("register")], summary=_("create account")),

)
class UserCreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema_view(
    post=extend_schema(tags=[_("accesslevel")], summary=_("create access leve")),
    update=extend_schema(tags=[_("accesslevel")], summary=_("update access leve")),
)
class AccessLevelViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = AccessLevel.objects.all()
    serializer_class = AccessLevelSerializer
    permission_classes = (IsAdminUser,)


@extend_schema_view(
    request_suggestions=extend_schema(tags=[_("suggestions")], summary=_("get suggestions of token")),
    get_request_suggestions=extend_schema(tags=[_("suggestions")], summary=(_("get suggestions")),
                                          parameters=[OpenApiParameter("request_id", OpenApiTypes.STR, required=True),
                                                      OpenApiParameter("xlsx", OpenApiTypes.BOOL, required=False,
                                                                       default=False, description="xlsx or json")]),

    request_datas=extend_schema(tags=[_("datas")], summary=_("get datas")),
    get_request_datas=extend_schema(tags=[_("datas")], summary=(_("get datas")),
                                    parameters=[OpenApiParameter("request_id", OpenApiTypes.STR, required=True),
                                                OpenApiParameter("xlsx", OpenApiTypes.BOOL, required=False,
                                                                 default=False, description="xlsx or json"), ], )

)
class RequestViewSet(GenericViewSet):
    queryset = AccessLevel.objects.all()
    permission_classes = (IsAuthenticated,)
    crawl_post = CrawlPost()
    static_suggestions = "resources/static/suggestions"
    static_data = "resources/static/datas"
    max_suggestions_count = 20
    page_count = 500

    def _http_response_to_xlsx(self, df, df_name, stream=io.BytesIO()):
        df.to_excel(stream, sheet_name=df_name, index=False, encoding='utf-8')
        response = HttpResponse(iter([stream.getvalue()]))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers["Content-Disposition"] = f"attachment; filename={df_name}.xlsx"
        return response

    def get_serializer_class(self):
        if self.action == 'request_suggestions':
            return SuggestionsSerializer
        else:
            return DatasSerializer

    @action(methods=['post'], detail=False)
    def request_datas(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        from_date = serializer.validated_data["from_date"]
        to_date = serializer.validated_data["to_date"]
        page = serializer.validated_data["page"]
        categories = serializer.validated_data.get("categories")
        city = serializer.validated_data.get("city")
        title = serializer.validated_data.get("title")
        try:
            access_level = self.get_queryset().get(user=self.request.user)
        except Exception:
            return Response("No access level defined for this user")
        if access_level.max_number_of_data is not None and access_level.max_number_of_data < 1:
            return Response(f"The number of your requests has been completed")
        if categories is not None:
            categories = [c for c in categories.strip().split(',')]
        request_id = str(uuid.uuid4())
        RequestHistory.create_request_history(user=self.request.user, request_id=request_id)
        return DatasResponse(data=request_id, request_id=request_id, static_datas=self.static_data,
                             from_date=from_date, to_date=to_date, categories=categories, city=city, title=title,
                             page=page, page_count=self.page_count, user=self.request.user)

    @action(methods=['get'], detail=False)
    def get_request_datas(self, *args, **kwargs):
        query_params = self.request.query_params
        request_id = query_params.get('request_id')
        is_xlsx = query_params.get('xlsx')
        fs = FileSystemStorage(
            base_url="/static/",
            location=settings.STATICFILES_DIRS[0]
        )
        if fs.exists(f"datas/{request_id}.json"):
            if is_xlsx == "true":
                df = pd.json_normalize(json.load(fs.open(f"datas/{request_id}.json")))
                return self._http_response_to_xlsx(df=df, df_name=request_id)
            return HttpResponse(fs.open(f"datas/{request_id}.json"),
                                content_type="application/json")
        else:
            try:
                status = RequestHistory.objects.get(request_id=request_id).status
                if not status:
                    return Response("sth went wrong, request for get datas again")
                return Response("process of getting datas not finished")
            except:
                return Response("invalid request_id")

    @action(methods=['post'], detail=False)
    def request_suggestions(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        try:
            access_level = self.get_queryset().get(user=self.request.user)
        except Exception:
            return Response("No access level defined for this user")
        if access_level.max_number_of_data is not None and access_level.max_number_of_data < 1:
            return Response(f"The number of your requests has been completed")
        status, response = self.crawl_post.get_post(token)
        if status != 1:
            return Response(f"{token} expired or is wrong")
        try:
            json_data = PostFormater(response).clean()["suggestions"][:self.max_suggestions_count]
        except Exception:
            return Response("has no suggestions")
        request_id = str(uuid.uuid4())
        RequestHistory.create_request_history(user=self.request.user, request_id=request_id,
                                              count_data=self.max_suggestions_count)
        access_level.update_max_number_of_data(len(json_data))
        return SuggestionsResponse(data=request_id, request_id=request_id, json_data=json_data,
                                   static_suggestions=self.static_suggestions)

    @action(methods=['get'], detail=False)
    def get_request_suggestions(self, *args, **kwargs):
        query_params = self.request.query_params
        request_id = query_params.get('request_id')
        is_xlsx = query_params.get('xlsx')
        fs = FileSystemStorage(
            base_url="/static/",
            location=settings.STATICFILES_DIRS[0]
        )
        if fs.exists(f"suggestions/{request_id}.json"):
            if is_xlsx == "true":
                df = pd.json_normalize(json.load(fs.open(f"suggestions/{request_id}.json")))
                return self._http_response_to_xlsx(df=df, df_name=request_id)
            return HttpResponse(fs.open(f"suggestions/{request_id}.json"),
                                content_type="application/json")
        else:
            try:
                status = RequestHistory.objects.get(request_id=request_id).status
                if not status:
                    return Response("sth went wrong, request for get suggestions again")
                return Response("process of getting suggestions not finished")
            except:
                return Response("invalid request_id")
