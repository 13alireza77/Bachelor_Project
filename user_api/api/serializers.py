from django.contrib.auth import get_user_model
from rest_framework import serializers

from user_api.models import AccessLevel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model()(**validated_data)
        user.set_password(password)
        user.save()
        AccessLevel.objects.create(user=user, max_number_of_data=0)
        return user


class AccessLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLevel
        fields = '__all__'


class DatasSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField(format="%Y-%m-%d  %H:%M:%S", required=True)
    to_date = serializers.DateTimeField(format="%Y-%m-%d  %H:%M:%S", required=True)
    page = serializers.IntegerField(required=True, help_text="page count is 100", min_value=0, allow_null=False)
    categories = serializers.CharField(max_length=50, allow_null=True, allow_blank=False, required=False,
                                       help_text="split categories by ',' ")
    city = serializers.CharField(required=False, allow_null=True, allow_blank=False, help_text="name of city")
    title = serializers.CharField(required=False, allow_null=True, allow_blank=False, help_text="or subtitle")
    type = serializers.CharField(required=False, max_length=10, help_text="data or dict")


class SuggestionsSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=15)
    type = serializers.CharField(required=False, max_length=10, help_text="data or dict")
