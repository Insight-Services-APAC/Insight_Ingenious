# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

EXPOSE 80

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir /ingen_app
COPY requirements.txt ./installs/requirements.txt

# In bash create a directory and copy the app into it
RUN pip install -r ./installs/requirements.txt

# Change to the app directory
WORKDIR /ingen_app
RUN python -c "from transformers import AutoTokenizer, AutoModel; \
           AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
           AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

CMD ["cat"]
