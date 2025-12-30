# Use official Python image as base
FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working dir
WORKDIR /app

# Install minimal build deps (if needed) and clean up
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Copy only requirements first for Docker layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project files
COPY . /app

# Create unprivileged user and set ownership
RUN groupadd -r app && useradd --no-log-init -r -g app app \
	&& chown -R app:app /app
USER app

# Do NOT hardcode API keys. Provide at runtime with -e or secrets.

# Default command to run the agent REPL
CMD ["python3", "-m", "app.agent"]
