# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13.1-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN apt update && apt install git
RUN git clone https://github.com/fluques/panns_inference.git
RUN python -m pip install panns-inference/.

WORKDIR /app
COPY . /app

