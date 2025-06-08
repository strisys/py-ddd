FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    build-essential \
    sudo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set working directory to model and install dependencies
WORKDIR /workspace/model

COPY model/requirements.txt ./requirements.txt
COPY model/setup.py ./setup.py
COPY model/pyproject.toml ./pyproject.toml
COPY model/src/ ./src/
COPY model/tests/ ./tests/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install build \
    && python -m build 

# Set up and install services
WORKDIR /workspace/services

COPY services/requirements.txt ./requirements.txt
COPY services/setup.py ./setup.py
COPY services/pyproject.toml ./pyproject.toml
COPY services/src/ ./src/
COPY services/tests/ ./tests/

RUN pip install --no-cache-dir -r requirements.txt 

# Copy shared validation script and run validation
COPY scripts/ /workspace/scripts/
RUN pip install pipdeptree \
    && python /workspace/scripts/validate_imports.py model/src model/requirements.txt \
    && python /workspace/scripts/validate_imports.py services/src services/requirements.txt \
    && pytest $(find . -type d -name tests) --maxfail=1 --tb=short

# Switch to non-root user
USER $USERNAME
