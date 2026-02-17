# Music Indexing and Retrieval

## Description.
Dockerized rest API to extract embeddings from music files. Index vector embeddings with Faiss. And query with an excerpt of audio for the nearest neighbors in the index.

## Components
- [Python](https://www.python.org/)
- [Nginx](https://nginx.org/)
- [Django](https://www.djangoproject.com/)
- [Librosa](https://librosa.org/)
- [Faiss](https://github.com/facebookresearch/faiss/)
- [Apache Kafka](https://kafka.apache.org/)
- [Postgres](https://www.postgresql.org/)


## Requirements
1. Docker and compose
    [Docker installation script](https://docs.docker.com/engine/install/ubuntu/)



## Installation
1. Clone the repository:
```bash
git clone https://github.com/fluques/music_indexing_retrieval.git
```
2. Enter directory:
```bash
cd music_indexing_retrieval
```
3. Set default settings:
```bash
cp .env.sample .env
```
4. Run docker-compose file:
```bash
docker compose -f .\compose.yaml  up --build --force-recreate
```

## Running service on:
```bash
http://127.0.0.1:8989
```


## Python usage

 ### Upload a mp3 file

```python 
import requests
from pathlib import Path

url = 'http://127.0.0.1:8989/api/audiofile/upload/'
file_path = file_path
file_name = Path(file_path).name
with open(file_path, 'rb') as f:
    headers={'Content-Disposition': 'attachment; filename=' + file_name}
    files = {'file':  f} 
    response = requests.put(url, files=files, headers=headers)
``` 

 ### Create the index

```python 
import requests
url = 'http://127.0.0.1:8989/api/audiofile/index_uploads/' 
response = requests.put(url)
``` 

 ### Save the index

```python 
import requests
url = 'http://127.0.0.1:8989/api/audiofile/save_index/'
requests.get(url)
``` 


### Search knn with excerpt of music
```python
import requests
import os
url = 'http://127.0.0.1:8989/api/audiofile/knn_search/'
file_path = 'query.mp3'
with open(file_path, 'rb') as f:
    headers={'Content-Disposition': 'attachment; filename=' + os.path.basename(file_path)}
    payload={"knn":3}
    files = {'file':  f} 
    response = requests.get(url, data=payload, files=files, headers=headers)
```


