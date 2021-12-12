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
        return user


class AccessLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLevel
        fields = '__all__'


class RequestSerializer(serializers.Serializer):
    from_date = serializers.DateField(format="%Y-%m-%d", required=True)
    to_date = serializers.DateField(format="%Y-%m-%d", required=True)
    categories = serializers.CharField(max_length=50, allow_null=True, allow_blank=False, required=False,
                                       help_text="split categories by ',' ")
    city = serializers.CharField(required=False, allow_null=True, allow_blank=False, help_text="name of city")
    title = serializers.CharField(required=False, allow_null=True, allow_blank=False)


class SuggestionsSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=15)
