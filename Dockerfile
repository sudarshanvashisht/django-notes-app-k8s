FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN groupadd -g 10001 appuser \
    && useradd -u 10001 -g appuser -m -s /bin/bash appuser

COPY --chown=appuser:appuser . .

# Run collectstatic so WhiteNoise can serve the React static files
RUN python manage.py collectstatic --noinput && chown -R appuser:appuser /app/staticfiles

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "notesapp.wsgi:application"]
