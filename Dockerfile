FROM node:20-alpine AS css-builder

WORKDIR /build

COPY package*.json ./
RUN npm ci

COPY tailwind.config.js postcss.config.js ./
COPY static/css/tailwind.css ./static/css/
COPY templates ./templates
COPY apps ./apps

RUN npm run build-css

FROM python:3.12.7-slim AS python-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

FROM python:3.12.7-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings.production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=python-builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . .
COPY --from=css-builder /build/static/css/style.css ./static/css/

RUN mkdir -p static_collected media logs /tmp && \
    chmod +x scripts/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["scripts/docker-entrypoint.sh"]
