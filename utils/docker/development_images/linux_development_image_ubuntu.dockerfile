# syntax=docker/dockerfile:1
FROM ubuntu:24.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# Expose port 80
EXPOSE 80

# Set the working directory
WORKDIR /ingen_app

# Add deadsnakes PPA and install Python 3.12
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.12 \
        wget \
        zsh \
        git \
        fonts-font-awesome \
        unixodbc \
        unixodbc-dev \
        libodbc2 \
        libodbccr2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Remove the externally-managed restriction
RUN rm /usr/lib/python*/EXTERNALLY-MANAGED

# Install pip independently
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

# Copy requirements and install dependencies with --break-system-packages
COPY requirements.txt /installs/requirements.txt
RUN pip install --break-system-packages -r /installs/requirements.txt

# Pre-download model files
RUN python3.12 -c "from transformers import AutoTokenizer, AutoModel; \
                   AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
                   AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# Install Oh My Zsh
RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

# Set the default shell to Zsh
SHELL ["/usr/bin/zsh", "-c"]

CMD ["zsh"]
