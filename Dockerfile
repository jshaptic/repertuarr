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

# We use the array syntax to ensure signals are passed correctly
CMD ["python", "main.py"]
