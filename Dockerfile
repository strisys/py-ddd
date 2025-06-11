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
ARG BUILD_CONTEXT=remote
ENV BUILD_CONTEXT=${BUILD_CONTEXT}

RUN groupadd --gid $USER_GID $USERNAME \
   && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
   && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
   && chmod 0440 /etc/sudoers.d/$USERNAME

# Upgrade pip once at the beginning
RUN pip install --no-cache-dir --upgrade pip build pipdeptree

# Set up and install model
WORKDIR /app/model

COPY model/requirements.txt ./requirements.txt
COPY model/setup.py ./setup.py
COPY model/pyproject.toml ./pyproject.toml
COPY model/src/ ./src/
COPY model/tests/ ./tests/

RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   python -m build; \
   fi

# Set up and install services
WORKDIR /app/services

COPY services/requirements.txt ./requirements.txt
COPY services/setup.py ./setup.py
COPY services/pyproject.toml ./pyproject.toml
COPY services/src/ ./src/
COPY services/tests/ ./tests/

RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   python -m build; \
   fi

# Set up and install api
WORKDIR /app/api

COPY api/requirements.txt ./requirements.txt
COPY api/setup.py ./setup.py
COPY api/pyproject.toml ./pyproject.toml
COPY api/src/ ./src/

RUN pip install --no-cache-dir -r requirements.txt

# Copy shared validation script and run validation
COPY scripts/ /app/scripts/

RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   python /app/scripts/run_all_tests.py; \
   fi

WORKDIR /app
ENV PYTHONPATH=/app/api/src:/app/services/src:/app/model/src

USER $USERNAME

EXPOSE 8080
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]
