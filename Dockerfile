# Docker image for homelab-bot.
#
# Config: set CONFIG_PATH to the mounted config file (default: /config/config.yaml).
# Ports:
#   WEBHOOK_PORT — Radarr/Sonarr/media-server webhooks (default: 8585 / bot.webhook_port)
#   WEB_UI_PORT  — admin UI at /admin (default: same as webhook port / bot.web_ui_port)
# Unraid example: map /mnt/user/appdata/homelab-bot -> /config
#                 Variable CONFIG_PATH=/config/config.yaml
#                 Variable WEBHOOK_PORT=8585
#                 Variable WEB_UI_PORT=8586   # optional; omit to share webhook port
#                 Port mappings for each listen port you expose
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
