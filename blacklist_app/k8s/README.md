# Manifiestos Kubernetes — blacklist_app

Manifiestos del laboratorio de Kubernetes (namespace `curso`).

## Estructura

```text
k8s/
├── 00-namespace.yaml         # Namespace curso
├── 10-postgres-config.yaml   # ConfigMap de Postgres
├── 20-postgres.yaml          # Service headless + StatefulSet + PVC
├── 30-app-deployment.yaml    # Deployment (init container, probes, no root)
└── 31-app-service.yaml       # Service NodePort
```

El Secret `blacklist-secret` **no** se versiona: se crea por comando (ver abajo).

## Despliegue (cuando haya clúster disponible)

```bash
# Desde blacklist_app/
kubectl apply -f k8s/00-namespace.yaml
kubectl config set-context --current --namespace=curso

kubectl create secret generic blacklist-secret \
  --from-literal=POSTGRES_PASSWORD=postgres-curso \
  --from-literal=BEARER_TOKEN=token-curso-k8s \
  --from-literal=DATABASE_URL=postgresql://postgres:postgres-curso@postgres:5432/blacklist_db

kubectl apply -f k8s/
kubectl get pods -w
```

## Acceso a la API

```bash
kubectl port-forward svc/blacklist-app 8080:80
curl http://localhost:8080/blacklists/ping
```

> **Nota:** en este entregable no se ejecutó minikube/kubectl en la máquina del curso (indicación del profesor). Quedan listos el ajuste del Dockerfile (UID `10001`) y los manifiestos.
