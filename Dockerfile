# Base stage - handles system dependencies and initial setup
FROM python:3.12-slim as base

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG BUILD_CONTEXT=remote

ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1 \
   PYTHONIOENCODING=utf-8 \
   LANG=C.UTF-8 \
   LC_ALL=C.UTF-8 \
   DEBIAN_FRONTEND=noninteractive \
   BUILD_CONTEXT=${BUILD_CONTEXT}

RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential \
   curl \
   wget && \
   if [ "$BUILD_CONTEXT" = "local" ]; then \
   apt-get install -y --no-install-recommends sudo; \
   fi && \
   curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
   apt-get install -y nodejs && \
   node --version && \
   npm --version && \
   apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip build pipdeptree

# Application stage - builds on base and adds user + application
FROM base as app

# Re-declare ARGs needed in this stage (ARGs don't carry over between stages)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG BUILD_CONTEXT=remote

# Create non-root user
RUN groupadd --gid $USER_GID $USERNAME \
   && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
   && mkdir -p /etc/sudoers.d \
   && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
   && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up and install model
WORKDIR /app/server/model
COPY server/model/ ./

RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   python -m build; \
   fi

# Set up and install services
WORKDIR /app/server/services
COPY server/services/ ./

RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   python -m build; \
   fi

# Set up and install api
WORKDIR /app/server/api
COPY server/api/ ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy shared validation script and run validation
WORKDIR /app
COPY scripts/ ./scripts

ENV PYTHONPATH=/app/server/api/src:/app/server/services/src:/app/server/model/src

RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   python ./scripts/run_all_tests.py; \
   fi

WORKDIR /app/client
COPY client/src/ ./src
COPY client/package.json ./package.json
COPY client/webpack.common.js ./webpack.common.js
COPY client/webpack.config.dev.js ./webpack.config.dev.js
COPY client/webpack.config.prod.js ./webpack.config.prod.js
RUN npm install

# Uninstall Node.js if not in local build context
RUN if [ "$BUILD_CONTEXT" != "local" ]; then \
   apt-get update && \
   apt-get remove -y nodejs && \
   apt-get autoremove -y && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/nodesource.list; \
   fi

USER $USERNAME

WORKDIR /app
EXPOSE 8080
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]