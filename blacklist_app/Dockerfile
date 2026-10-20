# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage base: resuelve e instala las dependencias de la aplicación
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS base

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=600 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.5

# Poetry con versión fija para que el build sea reproducible
RUN pip install --upgrade pip && \
    pip install --timeout=600 "poetry==${POETRY_VERSION}"

# Copiamos primero la configuración para aprovechar la caché de capas
COPY pyproject.toml poetry.lock* ./

# Instalamos en el Python del sistema, sin virtualenv dentro del contenedor
RUN poetry config virtualenvs.create false

# Solo dependencias de producción, sin instalar el paquete del proyecto
RUN poetry install --only main --no-root

# ---------------------------------------------------------------------------
# Stage tester: agrega las dependencias de desarrollo y corre las pruebas
# Uso: docker build --target tester -t blacklist-app:test .
# ---------------------------------------------------------------------------
FROM base AS tester

# No se definen DATABASE_URL ni BEARER_TOKEN aquí: tests/conftest.py las
# configura por su cuenta (SQLite temporal + token de prueba) antes de
# importar la aplicación.
RUN poetry install --with dev --no-root

COPY ./src /app/src
COPY ./tests /app/tests

CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"]

# ---------------------------------------------------------------------------
# Stage runner: imagen final mínima, sin herramientas de build ni dev deps
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3000

# Copiamos las librerías ya instaladas desde base (incluye gunicorn en /usr/local/bin)
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Código de la aplicación
COPY ./src /app/src

# Usuario sin privilegios con UID fijo (requerido por runAsNonRoot en Kubernetes)
RUN groupadd -r -g 10001 noroot && \
    useradd -r -u 10001 -g noroot noroot && \
    chown -R noroot:noroot /app

USER noroot

EXPOSE 3000

# Healthcheck contra el endpoint público /blacklists/ping (no requiere token).
# Usa urllib para no tener que instalar curl en la imagen slim.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; \
sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','3000')+'/blacklists/ping', timeout=4).status == 200 else sys.exit(1)"

# Render/Railway inyectan PORT; en local cae al default 3000
CMD ["sh", "-c", "gunicorn --preload -w 4 -b 0.0.0.0:${PORT} src.main:app"]
