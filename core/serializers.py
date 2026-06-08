from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PlatformApplication

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PlatformApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformApplication
        fields = '__all__'
        read_only_fields = ['applicant', 'status', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        print("后端接收原始data：", data)
        return super().to_internal_value(data)


