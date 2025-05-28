# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port 80
EXPOSE 80

# Set the working directory
WORKDIR /ingen_app

# Add deadsnakes PPA and install Python 3.12
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sudo \
        lsof \
        unixodbc \
        unixodbc-dev \
        libodbc2 \
        libodbccr2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy files into the container
COPY dist/ingenious-1.0.0-py3-none-any.whl /ingen_app/ingenious-1.0.0-py3-none-any.whl
RUN mkdir -p /ingen_app/ingenious/sample_dataset
RUN mkdir -p /ingen_app/ingenious/tmp
RUN mkdir -p /ingen_app/tmp
#RUN mkdir -p /ingen_app/public
#COPY public /ingen_app/public
COPY ingenious/sample_dataset/cleaned_students_performance.csv /ingen_app/ingenious/sample_dataset/cleaned_students_performance.csv

# Install dependencies
RUN pip install ./ingenious-1.0.0-py3-none-any.whl[ChatHistorySummariser]


# Set the command to run the app
CMD ["ingen_cli"]
