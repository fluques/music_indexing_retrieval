from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AudioFile, AudioSegmentRange


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'file_field_name', 'file_name', 'metadata', 'embeddings', 'uploaded_at']

class AudioSegmentRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioSegmentRange
        fields = ['id', 'audio_file', 'start_second', 'end_second']
        depth = 1