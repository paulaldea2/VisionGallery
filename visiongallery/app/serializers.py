from rest_framework import serializers
from app.models import *

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first', 'last', 'username']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first', 'last', 'email', 'username', 'phone', 'join_date']

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadModel
        fields = ['labels', 'objects_api', 'properties', 'text_image', 'location' , 'datetime']
