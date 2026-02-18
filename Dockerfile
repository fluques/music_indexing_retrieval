# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13.1-slim

EXPOSE 8000
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r  requirements.txt

RUN apt-get clean && apt-get -y update
RUN apt-get -y install nginx systemctl

RUN apt-get -y install ffmpeg


WORKDIR /app
COPY . /app



CMD ["/bin/sh", "-c", "systemctl start nginx && \
python manage.py makemigrations && \
python manage.py migrate && \
python manage.py collectstatic --noinput && \
python manage.py kafka_consumer & \
gunicorn --bind 0.0.0.0:8000 music_indexing_retrieval.wsgi:application"]
