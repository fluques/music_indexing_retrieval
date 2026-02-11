from .models import AudioFile
from django.http import JsonResponse
from .serializers import AudioFileSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
import asyncio
from .kafka_client import send_kafka_message
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class AudioFileListView(viewsets.ModelViewSet):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer

    @action(detail=False, methods=['put'],parser_classes=[FileUploadParser],url_path=r'upload')
    def upload_audio_file(self, request):
        file_obj = request.data['file']
        # Read the file's content into memory (bytes)
        file_obj.seek(0)
        file_content = file_obj.read()
        

        file_path = os.path.join('uploads', file_obj.name)
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        saved_path = default_storage.save(file_path, ContentFile(file_content))
        if saved_path:
            audio_file = AudioFile.objects.create(
                file_field_name=saved_path,
                file_name=file_obj.name,
            )
            #asyncio.run(send_kafka_message({'id': audio_file.id, 'file_name': audio_file.file_field_name}))
            return JsonResponse({"result": "File uploaded successfully", "id": audio_file.id,"file_path": audio_file.file_name}, status=201)
        return JsonResponse({}, status=400)