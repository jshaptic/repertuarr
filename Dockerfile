# Docker image for homelab-bot.
#
# Config: set CONFIG_PATH to the mounted config file (default: /config/config.yaml).
# Port (fixed): 8585 — webhooks + admin UI (/admin).
# Unraid example: map /mnt/user/appdata/homelab-bot -> /config
#                 Variable CONFIG_PATH=/config/config.yaml
#                 Port mapping: host:8585 -> container:8585
#
# Persist SQLite too: map a host path to /app/data (DB defaults to data/media_bot.db).

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for asyncssh or compilation)
# RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy only the files needed for dependency installation first
COPY pyproject.toml poetry.lock ./

# Install dependencies (no virtualenv for Docker)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV CONFIG_PATH=/config/config.yaml
EXPOSE 8585

# We use the array syntax to ensure signals are passed correctly
CMD ["python", "main.py"]
