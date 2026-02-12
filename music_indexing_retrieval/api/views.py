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
from pydub import AudioSegment
import soundfile as sf
import librosa
import numpy as np
from panns_inference import AudioTagging

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
            self.convert_mp3_to_wav(default_storage.path(saved_path))
            #asyncio.run(send_kafka_message({'id': audio_file.id, 'file_name': audio_file.file_field_name}))
            return JsonResponse({"result": "File uploaded successfully", "id": audio_file.id,"file_path": audio_file.file_name}, status=201)
        return JsonResponse({}, status=400)
    
    def convert_mp3_to_wav(self, file_path):
        model = AudioTagging(checkpoint_path=None, device='cpu') 
        # Define file paths
        output_file = file_path+".wav"

        # Convert MP3 to WAV using pydub
        try:
            sound = AudioSegment.from_mp3(file_path)
            sound.export(output_file, format="wav")
            print(f"Successfully converted {file_path} to {output_file}")
        except Exception as e:
            print(f"Error during conversion: {e}")

        # Now you can use librosa to load the newly created WAV file
        y, sr = librosa.load(output_file, sr=44100) # Use sr=None to preserve original sample rate
        print(f"Loaded with librosa: Sample rate = {sr} Hz, Duration = {len(y)/sr:.2f} seconds")

        query_audio = y[None, :]

        _, emb = model.inference(query_audio)


        # Normalize the embedding. This scales the embedding to have a length (magnitude) of 1, while maintaining its direction.
        normalized_v = self.normalize(emb[0])


        # Return the normalized embedding required for dot_product elastic similarity dense vector
        return normalized_v
        


    # Function to normalize a vector. Normalizing a vector 
    #means adjusting the values measured in different scales 
    #to a common scale.
    def normalize(self,v):
        # np.linalg.norm computes the vector's norm (magnitude). 
        #The norm is the total length of all vectors in a space.
        norm = np.linalg.norm(v)
        if norm == 0: 
                return v
        
        # Return the normalized vector.
        return v / norm