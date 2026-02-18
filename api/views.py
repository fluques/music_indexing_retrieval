import json
from pathlib import Path

import faiss

from django.conf import settings
from .models import AudioFile, AudioSegmentRange
from django.http import JsonResponse
from .serializers import AudioFileSerializer, AudioSegmentRangeSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser
import asyncio
from .kafka_client import send_kafka_message
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from pydub import AudioSegment
import soundfile as sf
import librosa
import numpy as np
from .utils.faiss_connection import get_faiss_index, reload_faiss_index

class AudioFileListView(viewsets.ModelViewSet):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer

    @action(detail=False, methods=['put'],parser_classes=[FileUploadParser],url_path=r'upload_index')
    def upload_audio_file_and_index(self, request):
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
                embeddings=False,
                metadata={}

            )
            wav_file = self.convert_mp3_to_wav(default_storage.path(saved_path))
            os.remove(default_storage.path(saved_path))
            embeddings, audio_segments = self.get_embeddings(audio_file,wav_file)
            os.remove(wav_file)
            self.index_embeddings(embeddings,audio_segments)
            

            #asyncio.run(send_kafka_message({'id': audio_file.id, 'file_name': audio_file.file_field_name}))
            return JsonResponse({"result": "File uploaded successfully", "id": audio_file.id,"file_path": audio_file.file_name}, status=201)
        return JsonResponse({}, status=400)
    
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
            return JsonResponse({"result": "File uploaded successfully", "file_path": file_obj.name}, status=201)
        return JsonResponse({}, status=400)
    
    @action(detail=False, methods=['put'],parser_classes=[FileUploadParser],url_path=r'index_uploads')
    def index_uploads(self, request):

        asyncio.run(send_kafka_message({}))

        '''_, mp3_paths = default_storage.listdir("uploads")
        indexed_files = []
        for mp3_path in mp3_paths:
            file_obj = os.path.join('uploads', mp3_path)
            file_name = os.path.basename(file_obj)
            audio_file = AudioFile.objects.create(
                file_field_name=file_obj,                
                file_name=file_name,
                embeddings=False,
                metadata={}

            )
            wav_file = self.convert_mp3_to_wav(default_storage.path(file_obj))
            os.remove(default_storage.path(file_obj))
            embeddings, audio_segments = self.get_embeddings(audio_file,wav_file)
            os.remove(wav_file)
            self.index_embeddings(embeddings,audio_segments)
            indexed_files.append(file_name)'''

    
        return JsonResponse({"result": "Begin indexing files successfully"}, status=201)


    def index_uploads_sync(self):
        _, mp3_paths = default_storage.listdir("uploads")
        indexed_files = []
        for mp3_path in mp3_paths:
            file_obj = os.path.join('uploads', mp3_path)
            file_name = os.path.basename(file_obj)
            audio_file = AudioFile.objects.create(
                file_field_name=file_obj,                
                file_name=file_name,
                embeddings=True,
                metadata={}

            )
            wav_file = self.convert_mp3_to_wav(default_storage.path(file_obj))
            os.remove(default_storage.path(file_obj))
            embeddings, audio_segments = self.get_embeddings(audio_file,wav_file)
            os.remove(wav_file)
            self.index_embeddings(embeddings,audio_segments)
            indexed_files.append(file_name)

    
        return JsonResponse({"result": "File uploaded successfully", "files": indexed_files}, status=201)



    @action(detail=False, methods=['get'],parser_classes=[MultiPartParser],url_path=r'knn_search')
    def knn_search(self, request):
        file_obj = request.FILES['file']
        knn = request.data['knn']

        file_obj.seek(0)
        file_content = file_obj.read()        

        file_path = os.path.join('uploads', file_obj.name)
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        saved_path = default_storage.save(file_path, ContentFile(file_content))
        if saved_path:
            wav_file = self.convert_mp3_to_wav(default_storage.path(saved_path))
            os.remove(default_storage.path(saved_path))
            embeddings, _ = self.get_embeddings(None,wav_file)
            os.remove(wav_file)
            faiss_index = get_faiss_index()
            if faiss_index is None:
                return
            D, I = faiss_index.search(embeddings, int(knn))

            resp = []
            for resp_i in range(len(I)):
                distance_i = D[resp_i]
                index_i = I[resp_i]
                for idx in range(len(index_i)):
                    idxaudio_segment = index_i[idx]
                    distance_audio_segment = distance_i[idx]
                    audio_segment = AudioSegmentRange.objects.get(pk=idxaudio_segment)
                    resp.append({"distance":str(distance_audio_segment),"audio_segment":AudioSegmentRangeSerializer(audio_segment).data})

            sorted_pairs = sorted(resp,key=lambda item: float(item["distance"]))

            return JsonResponse({"results": sorted_pairs}, status=201, json_dumps_params={'ensure_ascii': False},)
        return JsonResponse({}, status=400)
    

    @action(detail=False, methods=['get'],parser_classes=[MultiPartParser],url_path=r'save_index')
    def index_save(self, request):
        faiss_index= get_faiss_index()
        if faiss_index is None:
            return
        faiss.write_index(faiss_index,settings.FAISS_INDEX_PATH)
        return JsonResponse({"results":"index saved succesfully"}, status=201)
    
    @action(detail=False, methods=['get'],parser_classes=[MultiPartParser],url_path=r'reload_index')
    def reload_index(self, request):
        faiss_index= reload_faiss_index()
        return JsonResponse({"results":"index reloaded succesfully"}, status=201)

    def convert_mp3_to_wav(self, file_path):

        # Define file paths
        output_file = file_path+".wav"

        # Convert MP3 to WAV using pydub
        try:
            sound = None
            sound = AudioSegment.from_mp3(file_path)

            sound.set_frame_rate(44100)
            sound.export(output_file, format="wav")
            print(f"Successfully converted {file_path} to {output_file}")
        except Exception as e:
            print(f"Error during conversion: {e}")
        return output_file

        
    def get_embeddings(self,audio_file=None, file_path =None):
        y, sr = librosa.load(file_path, sr=44100) 
        print(f"Loaded with librosa: Sample rate = {sr} Hz, Duration = {len(y)/sr:.2f} seconds")
        y =librosa.util.normalize(y)
        audio_segments = []
        y=np.trim_zeros(y, 'f')
        embeddings = []
        chunk_size = sr * 20
        chunk_overlap = 4
        for i in range(0,len(y),chunk_size//chunk_overlap):

            chunk = y[i:i+chunk_size]
            if len(chunk) < chunk_size:
                break
                   
            cens = librosa.feature.chroma_cens(y=chunk, sr=sr, n_chroma=12, hop_length=512)
            cens = np.mean(cens.T,axis=0)
            cens = self.normalize(cens)

            embeddings.append(cens)
            if(audio_file):
                audio_segment = AudioSegmentRange()
                audio_segment.audio_file= audio_file
                audio_segment.start_second =i/sr
                audio_segment.end_second = (i+chunk_size)/sr
                audio_segments.append(audio_segment)
                
        return np.vstack(embeddings), audio_segments
    
    def normalize(self,v):
        norm = np.linalg.norm(v)
        if norm == 0: 
                return v
        return v / norm
    
    def index_embeddings(self, embeddings, audio_segments):
        faiss_index = get_faiss_index()
        if faiss_index is None:
            return
        #faiss_index.add_with_ids(embeddings, np.full(embeddings.shape[0], id))
        ids=[]
        for i in range(len(embeddings)):
            audio_segment=audio_segments[i]
            audio_segment.index_id = faiss_index.ntotal + i
            #ids.append(faiss_index.ntotal + i)
            audio_segment.save()
            
        faiss_index.add(embeddings)



