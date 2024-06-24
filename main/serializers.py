from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import FileUpload

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_ops', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'file', 'uploaded_at', 'uploaded_by']

    def validate_file(self, value):
        if value.name.split('.')[-1] not in ['pptx', 'docx', 'xlsx']:
            raise serializers.ValidationError("Only pptx, docx, and xlsx files are allowed.")
        return value
