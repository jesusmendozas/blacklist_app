# Informe: laboratorio Kubernetes — blacklist_app

## Integrantes

- Juan Camilo Díaz Zapateiro
- Rafael de Jesús Beleño Castellanos
- Yeison de Jesús Arrieta Venera
- Jesús Felipe Mendoza Salcedo

---

## Repositorio

- **GitHub:** [https://github.com/jesusmendozas/blacklist_app](https://github.com/jesusmendozas/blacklist_app)
- **Manifiestos:** [`blacklist_app/k8s/`](../blacklist_app/k8s/)
- **Dockerfile ajustado:** [`blacklist_app/Dockerfile`](../blacklist_app/Dockerfile)

---

## Objetivo

Preparar la aplicación `blacklist_app` para desplegarse en Kubernetes siguiendo la guía del laboratorio:

1. Ajustar el Dockerfile con UID numérico fijo (`10001`) para `runAsNonRoot`.
2. Escribir los manifiestos en `blacklist_app/k8s/`.
3. Documentar el despliegue y las pruebas de API previstas.

**Alcance de este entregable:** se omitió la instalación y uso de **minikube** / clúster local, según indicación del profesor (Kubernetes no está instalado en la máquina del curso). Quedan listos el Dockerfile y los manifiestos para aplicarlos cuando el entorno lo permita.

---

## Datos de la app relevantes para Kubernetes

| Dato | Valor | Implicación |
|------|-------|-------------|
| Stack | Flask + gunicorn (4 workers), Python 3.11 | ≥ 256 Mi de memoria |
| Puerto en el cluster | `8080` (`PORT=8080` en el Deployment) | `containerPort` / `targetPort` |
| Health check | `GET /blacklists/ping` (sin token) | readiness y liveness |
| Variables | `DATABASE_URL`, `BEARER_TOKEN` | Secret `blacklist-secret` |
| Base de datos | PostgreSQL 14 | StatefulSet + volumen |
| Arranque | `create_all` al iniciar | init container espera a Postgres |

---

## Paso 1 — Ajuste del Dockerfile (UID fijo)

Se cambió la creación del usuario `noroot` para fijar GID/UID `10001`:

```dockerfile
RUN groupadd -r -g 10001 noroot && \
    useradd -r -u 10001 -g noroot noroot && \
    chown -R noroot:noroot /app
```

**Por qué:** con `runAsNonRoot: true`, Kubernetes necesita un UID numérico. Sin UID fijo el Pod falla con `container has runAsNonRoot and image has non-numeric user`.

---

## Paso 4 — Manifiestos creados

```text
blacklist_app/k8s/
├── 00-namespace.yaml         # Namespace curso
├── 10-postgres-config.yaml   # ConfigMap (POSTGRES_DB, USER, PGDATA)
├── 20-postgres.yaml          # Service headless + StatefulSet + PVC 1Gi
├── 30-app-deployment.yaml    # Deployment (2 réplicas, init, probes, no root)
└── 31-app-service.yaml       # Service NodePort → targetPort 8080
```

| Archivo | Objetos | Práctica ilustrada |
|---------|---------|--------------------|
| `00-namespace.yaml` | Namespace `curso` | Aislamiento por ambiente |
| `10-postgres-config.yaml` | ConfigMap | Configuración fuera de la imagen |
| `20-postgres.yaml` | Service headless + StatefulSet + PVC | Estado con identidad y disco |
| `30-app-deployment.yaml` | Deployment | Init container, probes, recursos, no root |
| `31-app-service.yaml` | Service NodePort | Descubrimiento por labels |

El Secret con contraseñas **no** se versiona en Git: se crea por comando al desplegar.

**Detalle respecto a la guía:** en el Deployment se define `PORT=8080` porque la imagen usa la variable `PORT` (default `3000` en Docker Compose / Render). Así las probes en el puerto `8080` coinciden con el proceso gunicorn.

---

## Pasos omitidos (minikube / clúster)

No se ejecutaron en esta entrega (indicación del profesor):

- Paso 2: `minikube start` y addons
- Paso 3: `minikube image build -t blacklist-app:1.0 .`
- Paso 5: `kubectl apply` / verificación de pods
- Paso 6: port-forward y pruebas `curl` / Postman contra el cluster

Cuando haya clúster disponible, el orden previsto es:

```bash
cd blacklist_app

# Construir la imagen en el runtime del cluster (ejemplo minikube)
# minikube image build -t blacklist-app:1.0 .

kubectl apply -f k8s/00-namespace.yaml
kubectl config set-context --current --namespace=curso

kubectl create secret generic blacklist-secret \
  --from-literal=POSTGRES_PASSWORD=postgres-curso \
  --from-literal=BEARER_TOKEN=token-curso-k8s \
  --from-literal=DATABASE_URL=postgresql://postgres:postgres-curso@postgres:5432/blacklist_db

kubectl apply -f k8s/
kubectl get pods -w
```

### Verificación prevista

```bash
kubectl get all,pvc
kubectl rollout status deployment/blacklist-app
kubectl logs -l app=blacklist-app -c esperar-postgres
kubectl logs -l app=blacklist-app --tail=20
kubectl get endpoints blacklist-app
kubectl exec deploy/blacklist-app -- id   # uid=10001
```

### Pruebas de API previstas

```bash
kubectl port-forward svc/blacklist-app 8080:80

curl http://localhost:8080/blacklists/ping

curl -X POST http://localhost:8080/blacklists \
  -H "Authorization: Bearer token-curso-k8s" \
  -H "Content-Type: application/json" \
  -d '{"email":"spam@example.com","app_uuid":"123e4567-e89b-12d3-a456-426614174000","blocked_reason":"Spam"}'

curl http://localhost:8080/blacklists/spam@example.com \
  -H "Authorization: Bearer token-curso-k8s"

curl http://localhost:8080/blacklists/spam@example.com
```

Con Postman: importar `blacklist_app/postman/Blacklist_App.postman_collection.json` y el environment; usar `baseUrl` / `base_url` = `http://localhost:8080` y bearer token `token-curso-k8s`.

---

## Conclusión

Quedaron en el repositorio:

1. Dockerfile con UID `10001` compatible con `runAsNonRoot`.
2. Manifiestos Kubernetes completos bajo `blacklist_app/k8s/`.
3. Este informe con integrantes, estructura y comandos de despliegue/prueba.

La ejecución sobre minikube queda pendiente hasta que el entorno del curso permita instalar o usar Kubernetes.
