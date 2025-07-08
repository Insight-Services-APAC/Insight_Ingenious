FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    unixodbc \
    unixodbc-dev \
    ca-certificates \
    build-essential \
    git \
    ssh \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && mkdir -p /etc/odbc \
    && cp /opt/microsoft/msodbcsql18/etc/odbcinst.ini /etc/odbc/odbcinst.ini \
    && echo '/opt/microsoft/msodbcsql18/lib64' >> /etc/ld.so.conf.d/mssql.conf \
    && ldconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Create vscode user
RUN useradd --create-home --shell /bin/bash vscode \
    && mkdir -p /home/vscode/.ssh \
    && chown -R vscode:vscode /home/vscode

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Set working directory
WORKDIR /workspaces/ingenious

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ODBCSYSINI=/etc/odbc
ENV ODBCINI=/etc/odbc/odbc.ini

USER vscode
