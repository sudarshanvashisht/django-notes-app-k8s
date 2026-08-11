.PHONY: check test backend-test frontend-test build docker-build compose-config k8s-render

check:
	DJANGO_USE_SQLITE=true python3 manage.py check

backend-test:
	DJANGO_USE_SQLITE=true python3 manage.py test api

frontend-test:
	cd mynotes && npm run test:ci

build:
	cd mynotes && npm run build

test: check backend-test frontend-test build

docker-build:
	docker build -t sudarshan0907/notes-app-k8s:latest .

compose-config:
	docker compose config

k8s-render:
	kubectl kustomize k8s > /dev/null
