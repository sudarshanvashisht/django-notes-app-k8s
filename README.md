# Django Notes App — Production-Grade DevSecOps on Kubernetes

> A full-stack Django REST API + React notes application, containerized with Docker, orchestrated on Kubernetes, and deployed through a fully automated Jenkins CI/CD pipeline with security hardening, self-healing infrastructure, and GitOps-style deployments.

---

## 🏗️ Architecture Overview

```
                          ┌──────────────────────────────┐
                          │       GitHub Repository       │
                          │   (Source Code + K8s Manifests)│
                          └──────────────┬───────────────┘
                                         │  Webhook / Poll
                                         ▼
                          ┌──────────────────────────────┐
                          │     Jenkins CI/CD Pipeline     │
                          │  ┌──────────────────────────┐ │
                          │  │ 1. Clone Code            │ │
                          │  │ 2. Build Docker Image    │ │
                          │  │ 3. Run Unit Tests        │ │
                          │  │ 4. Compose Smoke Test    │ │
                          │  │ 5. Push to Docker Hub    │ │
                          │  │ 6. Deploy to Kubernetes  │ │
                          │  └──────────────────────────┘ │
                          └──────────────┬───────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
           ┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
           │  Docker Hub   │   │ Kind K8s Cluster  │   │ Compose Test │
           │  Registry     │   │  (Production)     │   │  (Staging)   │
           └──────────────┘   └────────┬─────────┘   └──────────────┘
                                       │
                              ┌────────┴────────┐
                              ▼                 ▼
                     ┌──────────────┐  ┌──────────────┐
                     │  Django Pods  │  │  MySQL Pod    │
                     │  (2 Replicas) │  │  (Persistent) │
                     └──────────────┘  └──────────────┘
```

---

## 🚀 Tech Stack

| Layer            | Technology                                                     |
| ---------------- | -------------------------------------------------------------- |
| **Frontend**     | React (pre-built static bundle served via Django)              |
| **Backend**      | Django REST Framework + Gunicorn WSGI                          |
| **Database**     | MySQL 8.0 with Persistent Volume Claims                        |
| **Reverse Proxy**| Nginx (local dev) / Kubernetes Ingress (production)            |
| **Container**    | Docker (multi-stage, non-root user)                            |
| **Orchestration**| Kubernetes (Kind cluster) with Namespace isolation             |
| **CI/CD**        | Jenkins Declarative Pipeline (6-stage)                         |
| **Registry**     | Docker Hub (`sudarshan0907/notes-app-k8s`)                     |

---

## 🔒 DevSecOps Security Hardening

### Non-Root Container Execution
The application container runs as a dedicated non-privileged user (`appuser`, UID 10001) instead of root, significantly reducing the attack surface for container escape exploits.

```dockerfile
# Security: Create non-root application user
RUN groupadd -g 10001 appuser \
    && useradd -u 10001 -g appuser -m -s /bin/bash appuser \
    && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser
```

### Kubernetes Secret Management
All database credentials (`MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`) are stored in Kubernetes Secrets and injected at runtime via `envFrom` — never hardcoded in source code or container images.

### `.env` Exclusion
The `.env` file is excluded from version control via `.gitignore` and is never committed to the repository. A `.env.example` template is provided for onboarding.

---

## ☸️ Kubernetes Manifests

All manifests are in the `k8s/` directory and deploy into the `notes-app` namespace:

| Manifest                  | Purpose                                                    |
| ------------------------- | ---------------------------------------------------------- |
| `namespace.yml`           | Creates the `notes-app` namespace for workload isolation   |
| `mysql-secret.yml`        | Stores database credentials as Kubernetes Secrets          |
| `mysql-pvc.yml`           | Provisions persistent storage for MySQL data               |
| `mysql-deployment.yml`    | MySQL 8.0 with `Recreate` strategy and health probes       |
| `mysql-service.yml`       | ClusterIP service for internal database connectivity       |
| `deployment.yml`          | Django app (2 replicas) with liveness/readiness probes     |
| `service.yml`             | ClusterIP service exposing Django on port 8000             |
| `ingress.yml`             | Nginx Ingress routing external HTTP traffic to the service |

### Self-Healing Infrastructure

**Django Pods** — HTTP-based health probes:
```yaml
livenessProbe:
  httpGet:
    path: /api/
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
```

**MySQL Pod** — Command execution probes:
```yaml
livenessProbe:
  exec:
    command: ["mysqladmin", "ping", "-h", "localhost"]
  initialDelaySeconds: 30
  periodSeconds: 10
```

### MySQL Recreate Strategy
The MySQL deployment uses `strategy.type: Recreate` instead of `RollingUpdate` to prevent **Persistent Volume deadlocks** — a single-replica database with `ReadWriteOnce` PVC would crash-loop during rolling updates because both old and new pods try to lock the same data files simultaneously.

---

## 🔄 Jenkins CI/CD Pipeline

The `Jenkinsfile` defines a **6-stage declarative pipeline** with GitOps-style deployments:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Clone Code  │───▶│ Build Image │───▶│ Unit Tests  │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Deploy K8s  │◀───│ Push to Hub │◀───│Compose Test │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Pipeline Stages

| Stage                    | Description                                                         |
| ------------------------ | ------------------------------------------------------------------- |
| **Clone Code**           | Checks out the `main` branch from GitHub                            |
| **Build Docker Image**   | Builds and tags with Git commit SHA (`sudarshan0907/notes-app-k8s:<sha>`) |
| **Run Unit Tests**       | Executes Django REST API tests inside the container (SQLite in-memory) |
| **Test & Run via Compose** | Smoke tests the full stack (Django + MySQL + Nginx) via Docker Compose |
| **Push to Docker Hub**   | Pushes both `:<sha>` and `:latest` tags to Docker Hub               |
| **Deploy to Kubernetes** | Loads image into Kind nodes, injects tag via `sed`, applies manifests |

### Dynamic Image Tagging
Every build is tagged with the **Git commit SHA** (`git rev-parse --short HEAD`), ensuring:
- Full traceability from deployed pod → Docker image → exact source code commit
- No ambiguous `:latest` tags in production
- Easy rollback to any previous version

```groovy
environment {
    IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
}
```

---

## 🧪 Automated Testing

### Django REST API Unit Tests
Located in `api/tests.py`, the test suite validates all CRUD endpoints:

| Test Case                | Endpoint Tested          | Assertion                        |
| ------------------------ | ------------------------ | -------------------------------- |
| `test_get_all_notes`     | `GET /api/notes/`        | Returns HTTP 200                 |
| `test_get_single_note`   | `GET /api/notes/<id>/`   | Returns correct note data        |
| `test_create_note`       | `POST /api/notes/create/`| Creates note, count increments   |
| `test_update_note`       | `PUT /api/notes/<id>/update/` | Updates title in database   |
| `test_delete_note`       | `DELETE /api/notes/<id>/delete/` | Removes note, count = 0 |
| `test_get_api_routes`    | `GET /api/`              | Returns API route listing        |

### Test Database Isolation
Tests run against an **in-memory SQLite database** to eliminate MySQL dependency during CI:
```python
import sys

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
```

---

## 📁 Project Structure

```
django-notes-app-k8s/
├── api/                        # Django REST API application
│   ├── models.py               # Note data model
│   ├── views.py                # CRUD API views
│   ├── serializers.py          # DRF serializers
│   ├── urls.py                 # API URL routing
│   └── tests.py                # Automated unit tests (6 test cases)
│
├── notesapp/                   # Django project configuration
│   ├── settings.py             # Environment-driven settings + test DB fallback
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI entry point for Gunicorn
│
├── mynotes/                    # React frontend (pre-built)
│   └── build/                  # Static production bundle
│
├── nginx/                      # Reverse proxy configuration
│   └── default.conf            # Nginx config for local dev
│
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yml           # Namespace isolation
│   ├── mysql-secret.yml        # Database credentials (base64)
│   ├── mysql-pvc.yml           # Persistent volume claim
│   ├── mysql-deployment.yml    # MySQL with Recreate strategy + probes
│   ├── mysql-service.yml       # Internal database service
│   ├── deployment.yml          # Django app with health probes
│   ├── service.yml             # Application ClusterIP service
│   └── ingress.yml             # HTTP traffic routing
│
├── Dockerfile                  # Hardened container (non-root user)
├── docker-compose.yml          # Local development orchestration
├── Jenkinsfile                 # 6-stage CI/CD pipeline
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── .gitignore                  # Git exclusions
```

---

## 🛠️ Getting Started

### Prerequisites
- Docker & Docker Compose
- Kubernetes cluster (Kind, Minikube, or cloud)
- Jenkins (with Docker socket access)
- `kubectl` configured

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/sudarshanvashisht/django-notes-app-k8s.git
cd django-notes-app-k8s
```

### 2️⃣ Local Development (Docker Compose)
```bash
cp .env.example .env
# Edit .env with your database credentials
docker compose up -d
```
Access the app at `http://localhost`

### 3️⃣ Run Unit Tests
```bash
docker build . -t notes-app-k8s:test
docker run --rm notes-app-k8s:test python manage.py test
```

### 4️⃣ Deploy to Kubernetes
```bash
# Create namespace and secrets
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/mysql-secret.yml

# Deploy the full stack
kubectl apply -f k8s/

# Verify deployment
kubectl get pods -n notes-app
kubectl get svc -n notes-app
```

---

## 🔑 Environment Variables

| Variable                | Description                    | Default           |
| ----------------------- | ------------------------------ | ----------------- |
| `DJANGO_SECRET_KEY`     | Django cryptographic key       | Dev-only fallback |
| `DJANGO_DEBUG`          | Enable/disable debug mode      | `False`           |
| `DJANGO_ALLOWED_HOSTS`  | Comma-separated allowed hosts  | `localhost`       |
| `MYSQL_DATABASE`        | Database name                  | `notesdb`         |
| `MYSQL_USER`            | Database user                  | `notesuser`       |
| `MYSQL_PASSWORD`        | Database password              | —                 |
| `MYSQL_ROOT_PASSWORD`   | MySQL root password            | —                 |
| `MYSQL_HOST`            | Database hostname              | `mysql`           |
| `MYSQL_PORT`            | Database port                  | `3306`            |
| `CORS_ALLOWED_ORIGINS`  | Frontend CORS origins          | `http://localhost` |
| `CSRF_TRUSTED_ORIGINS`  | Trusted CSRF origins           | `http://localhost` |

---

## 🐳 Docker Hub

**Image:** [`sudarshan0907/notes-app-k8s`](https://hub.docker.com/r/sudarshan0907/notes-app-k8s)

```bash
docker pull sudarshan0907/notes-app-k8s:latest
```

---

## 📝 Key Engineering Decisions

| Decision | Rationale |
|---|---|
| **Non-root Dockerfile** | Prevents container escape exploits; follows CIS Docker Benchmark |
| **Git SHA image tags** | Full traceability from pod → image → source commit |
| **SQLite test fallback** | Eliminates MySQL dependency in CI; tests run in < 5 seconds |
| **MySQL Recreate strategy** | Prevents PV deadlock on single-replica database rolling updates |
| **`DJANGO_ALLOWED_HOSTS: "*"`** | Required for K8s health probes which use internal pod IPs |
| **`imagePullPolicy: IfNotPresent`** | Optimized for local Kind clusters using `kind load docker-image` |
| **Ingress resource** | Layer 7 HTTP routing without NodePort exposure |

---

## 👤 Author

**Sudarshan Vashisht**

- GitHub: [@sudarshanvashisht](https://github.com/sudarshanvashisht)
- Docker Hub: [sudarshan0907](https://hub.docker.com/u/sudarshan0907)