from django.apps import AppConfig
from .utils.faiss_connection import load_or_create_faiss_index


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        faiss_index = load_or_create_faiss_index()
