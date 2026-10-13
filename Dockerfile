FROM python:3.12-slim

# Install system dependencies for MySQL client and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY backend/ ./backend/
COPY db/ ./db/
COPY api/ ./api/

WORKDIR /app/backend

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.dev

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
