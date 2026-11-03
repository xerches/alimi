# The Alimi platform image. Build context is the repo root (see docker-compose.yml) because the
# app imports tools/scanner and reads config/ and the policy library in policies/ at runtime.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 ALIMI_REPO_ROOT=/srv/alimi
WORKDIR /srv/alimi

COPY tools/scanner tools/scanner
COPY platform platform
# Editable install for the scanner: its mock connector finds fixtures/ next to its source folder.
RUN pip install -e ./tools/scanner ./platform

COPY config config
COPY policies/*.md policies/requirements.yaml policies/

RUN useradd --system --uid 10001 alimi && mkdir -p /var/lib/alimi && chown alimi /var/lib/alimi
USER alimi

EXPOSE 8000
CMD ["sh", "-c", "python -m alimi_platform.manage ensure-keys && python -m alimi_platform.manage init && uvicorn alimi_platform.asgi:app --host 0.0.0.0 --port 8000"]
