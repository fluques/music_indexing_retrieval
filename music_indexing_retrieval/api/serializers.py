from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AudioFile


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'file_field_name', 'file_name', 'metadata', 'embeddings', 'uploaded_at']