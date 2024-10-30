# syntax=docker/dockerfile:1
FROM ubuntu:24.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv

# Expose port 80
EXPOSE 80

# Install system dependencies and create a virtual environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3.12-venv \
        wget \
        zsh \
        git \
        fonts-font-awesome && \
    python3 -m venv $VIRTUAL_ENV && \
    . $VIRTUAL_ENV/bin/activate && \
    pip install --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt /installs/requirements.txt
RUN . $VIRTUAL_ENV/bin/activate && \
    pip install -r /installs/requirements.txt

# Pre-download model files
RUN . $VIRTUAL_ENV/bin/activate && \
    python3 -c "from transformers import AutoTokenizer, AutoModel; \
                AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
                AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# Install Oh My Zsh
RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

# Set the working directory
WORKDIR /ingen_app

# Set the default shell to Zsh
SHELL ["/usr/bin/zsh", "-c"]

CMD ["zsh"]
