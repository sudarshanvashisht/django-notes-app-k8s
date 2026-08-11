# Django Notes App K8s

Production-style notes app built with Django REST Framework, React, Docker, Jenkins, and Kubernetes.

## What’s included

- Django REST API for notes CRUD
- React SPA for the UI
- Gunicorn app server with WhiteNoise for static assets
- MySQL-backed persistence
- Kubernetes manifests with probes, resource limits, and kustomize
- Docker Compose for local full-stack runs
- CI checks for backend, frontend, Docker image build, and Kubernetes render

## Architecture

- React builds into `mynotes/build`
- Django serves the SPA and exposes `/api/*`
- MySQL stores note data
- Kubernetes runs the app behind a ClusterIP service
- The app image defaults to `sudarshan0907/notes-app-k8s:latest`

## Local development

Create a `.env` file from the example and fill in MySQL credentials.

```bash
cp .env.example .env
```

Run the stack:

```bash
docker compose up --build
```

The app is available through the Nginx container at `http://localhost`.

## Backend checks

```bash
DJANGO_USE_SQLITE=true python3 manage.py check
DJANGO_USE_SQLITE=true python3 manage.py test api
```

## Frontend checks

```bash
cd mynotes
npm ci
npm run test:ci
npm run build
```

## Docker image

Build the runtime image:

```bash
docker build -t sudarshan0907/notes-app-k8s:latest .
```

## Kubernetes

Render the manifests through kustomize:

```bash
kubectl kustomize k8s
```

Apply them with:

```bash
kubectl apply -k k8s
```

The deployment includes:

- `/api/healthz/` liveness probe
- `/api/readyz/` readiness probe
- init migration step
- resource requests and limits
- dedicated ConfigMap and Secret separation

If you change the image tag, update `k8s/kustomization.yml` or override it in your pipeline.

## CI/CD

The repository contains a Jenkins pipeline and a GitHub Actions workflow that:

- checks Django
- runs Django API tests
- runs the React test/build flow
- builds the Docker image
- renders Kubernetes manifests

## Environment variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_DB_ENGINE`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

## Notes

- `k8s/mysql-secret.yml` contains placeholder values only. Replace them for any real deployment.
- The API is intentionally public for demo purposes. Add authentication if you want a multi-user or production-private variant.
