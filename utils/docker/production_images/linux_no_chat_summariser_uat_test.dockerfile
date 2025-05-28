# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port 80
EXPOSE 80

# Set the working directory
WORKDIR /ingen_app

# Add required dependencies
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

# Copy the local `ingenious` and `ingenious_extensions` directories into the container
COPY ./ingenious /ingen_app/ingenious
COPY ./ingenious_extensions /ingen_app/ingenious_extensions

# Copy the `pyproject.toml` file into the container's working directory
COPY ./pyproject.toml /ingen_app/

# Update the `pyproject.toml` file to reference the `ingenious` package
WORKDIR /ingen_app/ingenious

# Use pip to install the project dependencies
RUN pip install ..

# Set the command to run the app
CMD ["ingen_cli"]
